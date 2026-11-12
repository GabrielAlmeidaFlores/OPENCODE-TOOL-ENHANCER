"""
Install, uninstall, and rollback orchestration.

Public API: :func:`plan_files`, :func:`install`, :func:`uninstall`,
:func:`list_backups`, :func:`source_metadata`, and :func:`source_digest`.

Side effects: commands with ``apply=True`` write into the target project and
delegate to the repository's shell installer. Nothing is staged or committed.

Module constants: ``STATE_SCHEMA_VERSION`` versions the state file.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__
from .locking import PlannedFile, build_lock, lock_drift, read_lock, sha256_file, write_json
from .paths import OteError, backup_root, is_within, lock_path, state_path
from .process import capture, git_commit, git_dirty, git_remote, run

STATE_SCHEMA_VERSION = 1


def _is_generated(path: Path) -> bool:
    """
    Return True for cache and operating-system files that must never be installed.
    """
    return (
        path.name == ".DS_Store"
        or path.suffix in {".pyc", ".pyo"}
        or "__pycache__" in path.parts
        or "node_modules" in path.parts
    )


def plan_files(root: Path, target: Path, components: list[str]) -> list[PlannedFile]:
    """
    Return every file the selected components write into the target.
    """
    planned: list[PlannedFile] = []

    def add(source: Path, destination: Path, component: str) -> None:
        """
        Record one planned file.
        """
        planned.append(PlannedFile(source=source, destination=destination, component=component))

    if "opencode" in components:
        add(
            root / "configs/opencode/opencode.jsonc",
            target / ".opencode/opencode.jsonc",
            "opencode",
        )
    if "agents" in components:
        for source in sorted((root / "agents").glob("*/AGENT.md")):
            add(source, target / ".opencode/agents" / f"{source.parent.name}.md", "agents")
    if "commands" in components:
        for source in sorted((root / "commands").glob("*.md")):
            add(source, target / ".opencode/commands" / source.name, "commands")
    if "skills" in components:
        for source in sorted((root / "skills").glob("*/SKILL.md")):
            name = source.parent.name
            for file in sorted(source.parent.rglob("*")):
                if file.is_file() and not _is_generated(file):
                    relative = file.relative_to(source.parent)
                    add(file, target / ".opencode/skills" / name / relative, "skills")
    if "ralph" in components:
        add(root / "configs/ralph/ralph.yml", target / ".ralph/ralph.yml", "ralph")
        for source in sorted((root / "configs/ralph/hats").glob("*.yml")):
            add(source, target / ".ralph/hats" / source.name, "ralph")

    for item in planned:
        if not item.source.is_file():
            raise OteError(f"missing source file: {item.source}")
    return planned


def summarize(planned: list[PlannedFile], target: Path) -> dict[str, int]:
    """
    Count new, updated, and unchanged destination files.
    """
    summary = {"new": 0, "updated": 0, "unchanged": 0}
    for item in planned:
        if not item.destination.is_file():
            summary["new"] += 1
        elif sha256_file(item.destination) == sha256_file(item.source):
            summary["unchanged"] += 1
        else:
            summary["updated"] += 1
    return summary


def source_metadata(root: Path) -> dict[str, str]:
    """
    Return the source repository, commit, version, and dirty flag recorded in the lock.
    """
    return {
        "repository": git_remote(root) or "https://github.com/GabrielAlmeidaFlores/OPENCODE-TOOL-ENHANCER",
        "commit": git_commit(root) or "unknown",
        "version": __version__,
        "dirty": "true" if git_dirty(root) else "false",
    }


def source_digest(planned: list[PlannedFile], target: Path) -> str:
    """
    Return a digest over the planned source contents and destinations.
    """
    digest = hashlib.sha256()
    for item in sorted(planned, key=lambda entry: entry.destination.relative_to(target).as_posix()):
        relative = item.destination.relative_to(target).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256_file(item.source).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def _is_current(
    lock: dict[str, Any] | None,
    target: Path,
    profile: str,
    components: list[str],
    planned: list[PlannedFile],
) -> bool:
    """
    Return True when the lock matches the source contents, profile, components, and files.
    """
    if not lock:
        return False
    if lock.get("profile") != profile or lock.get("components") != components:
        return False
    source = lock.get("source", {})
    if source.get("digest") != source_digest(planned, target):
        return False
    return not lock_drift(lock, target)


def _backup(root: Path, target: Path, stamp: str) -> Path | None:
    """
    Archive the existing project configuration before an apply step.
    """
    if not (target / ".opencode").exists() and not (target / ".ralph").exists():
        return None
    destination = backup_root(target) / stamp
    script = root / "scripts/maintenance/backup-config.sh"
    if not script.is_file():
        raise OteError(f"backup script not found: {script}")
    run(["bash", str(script), "--project-only", str(destination)], cwd=target)
    return destination


def _write_state(target: Path, payload: dict[str, Any]) -> None:
    """
    Persist the last operation for rerun memory and rollback.
    """
    write_json(state_path(target), payload)


def _run_installer(root: Path, target: Path, components: list[str], apply: bool, clean: bool) -> str:
    """
    Invoke the repository installer and return its combined output.
    """
    script = root / "scripts/installation/install.sh"
    command = [
        "bash",
        str(script),
        "--apply" if apply else "--dry-run",
        "--only",
        ",".join(components),
        "--target",
        str(target),
    ]
    if clean:
        command.append("--clean")
    code, stdout, stderr = capture(command, cwd=root)
    if code != 0:
        raise OteError(f"installer failed with exit {code}:\n{stdout}\n{stderr}")
    return "\n".join(part for part in (stdout, stderr) if part)


def install(
    root: Path,
    target: Path,
    profile: str,
    components: list[str],
    apply: bool,
    force: bool = False,
    clean: bool = False,
) -> dict[str, Any]:
    """
    Plan or perform an installation and return a machine-readable result.
    """
    planned = plan_files(root, target, components)
    summary = summarize(planned, target)
    existing_lock = read_lock(lock_path(target))
    current = _is_current(existing_lock, target, profile, components, planned)

    result: dict[str, Any] = {
        "target": str(target),
        "profile": profile,
        "components": components,
        "planned": [item.destination.relative_to(target).as_posix() for item in planned],
        "summary": summary,
        "current": current,
        "applied": False,
    }

    if not apply:
        result["output"] = _run_installer(root, target, components, apply=False, clean=clean)
        return result

    if current and not force:
        if existing_lock is not None:
            existing_lock["source"] = source_metadata(root)
            existing_lock["source"]["digest"] = source_digest(planned, target)
            write_json(lock_path(target), existing_lock)
        result["message"] = "already up to date"
        return result

    target.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = _backup(root, target, stamp)
    result["backup"] = str(backup) if backup else None

    result["output"] = _run_installer(root, target, components, apply=True, clean=clean)

    missing = [item.destination for item in planned if not item.destination.is_file()]
    if missing:
        raise OteError(f"installer did not create {len(missing)} planned file(s): {missing[0]}")

    lock = build_lock(root, target, profile, components, planned, source_metadata(root))
    lock["source"]["digest"] = source_digest(planned, target)
    write_json(lock_path(target), lock)
    _write_state(
        target,
        {
            "schema_version": STATE_SCHEMA_VERSION,
            "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "last_operation": "install",
            "target": str(target),
            "profile": profile,
            "components": components,
            "backup": str(backup) if backup else None,
        },
    )
    result["applied"] = True
    result["lock"] = str(lock_path(target))
    return result


def uninstall(
    target: Path,
    apply: bool,
    force: bool = False,
    purge: bool = False,
) -> dict[str, Any]:
    """
    Plan or remove every file recorded in the lock.
    """
    lock = read_lock(lock_path(target))
    if lock is None:
        raise OteError(f"no lock file found at {lock_path(target)}; nothing to uninstall")

    removable: list[str] = []
    skipped: list[dict[str, str]] = []
    for entry in lock.get("files", []):
        relative = entry.get("path", "")
        path = target / relative
        if not is_within(path, target):
            raise OteError(f"lock entry escapes the target: {relative}")
        if not path.is_file():
            continue
        if not force and sha256_file(path) != entry.get("sha256"):
            skipped.append({"path": relative, "status": "modified"})
            continue
        removable.append(relative)

    result: dict[str, Any] = {
        "target": str(target),
        "removable": removable,
        "skipped": skipped,
        "applied": False,
    }

    if not apply:
        return result

    for relative in removable:
        (target / relative).unlink()

    directories = sorted(
        {
            (target / relative).parent
            for relative in removable
        },
        key=lambda path: len(path.parts),
        reverse=True,
    )
    for directory in directories:
        current = directory
        while is_within(current, target) and current != target:
            try:
                current.rmdir()
            except OSError:
                break
            current = current.parent

    if purge:
        shutil.rmtree(target / ".ote", ignore_errors=True)
        lock_path(target).unlink(missing_ok=True)
        result["purged"] = True
    else:
        _write_state(
            target,
            {
                "schema_version": STATE_SCHEMA_VERSION,
                "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "last_operation": "uninstall",
                "target": str(target),
            },
        )
    result["applied"] = True
    return result


def list_backups(target: Path) -> list[dict[str, Any]]:
    """
    Return the CLI backups available for a target project, newest first.
    """
    root = backup_root(target)
    if not root.is_dir():
        return []
    backups: list[dict[str, Any]] = []
    for directory in sorted(root.iterdir(), reverse=True):
        if not directory.is_dir():
            continue
        archives = sorted(path.name for path in directory.glob("*.tar.gz"))
        backups.append({"path": str(directory), "archives": archives})
    return backups


def read_state(target: Path) -> dict[str, Any] | None:
    """
    Read the last operation state, if present.
    """
    path = state_path(target)
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    return data if isinstance(data, dict) else None
