"""
Install, uninstall, and rollback orchestration.

Public API: :func:`plan_files`, :func:`install`, :func:`uninstall`,
:func:`list_backups`, :func:`source_metadata`, and :func:`source_digest`.

Side effects: commands with ``apply=True`` write into the target project and
delegate to the repository's shell installer. Nothing is staged or committed.

Module constants: ``STATE_SCHEMA_VERSION`` versions the state file.
"""
from __future__ import annotations
from .constants import GENERATED_FILES_MESSAGE as MESSAGE_GENERATED_FILES
from .constants import GENERATED_PLAN_MESSAGE as MESSAGE_GENERATED_PLAN
from .constants import KEY_FILES as BACKUP_FILES_DIR
from .constants import KEY_ASCII as ASCII
from .constants import TEXT_SCRIPTS_INSTALLATION_INSTALL_SH as INSTALL_SCRIPT
from .constants import TEXT_STATE_JSON as STATE_FILE
from .constants import TEXT_TEXT_5 as SEPARATOR_COMMA

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .constants import (
    FALSE_VALUE,
    TRUE_VALUE,
    DEFAULT_ADAPTER,
    EMPTY_STRING,
    ENCODING_UTF8,
    NEWLINE,
    STATUS_FAIL,
    STATUS_MISSING,
    STATUS_MODIFIED,
    STATUS_NEW,
    STATUS_OK,
    STATUS_UNCHANGED,
    STATUS_UPDATED,
    OPERATION_INSTALL,
    OPERATION_UNINSTALL,
    FLAG_APPLY,
    FLAG_CLEAN,
    FLAG_DRY_RUN,
    FLAG_FORCE,
    FLAG_ONLY,
    FLAG_PROFILE,
    FLAG_TARGET,
    FLAG_TYPE,
    FLAG_YES,
    KEY_ADAPTER,
    KEY_ADAPTERS,
    KEY_APPLIED,
    KEY_ARCHIVES,
    KEY_ARTIFACTS,
    KEY_BACKUP,
    KEY_COMMIT,
    KEY_COMPONENT,
    KEY_COMPONENTS,
    KEY_CREATED,
    KEY_CURRENT,
    KEY_DETAIL,
    KEY_DIGEST,
    KEY_DIRTY,
    KEY_FAILURES,
    KEY_FEATURE,
    KEY_FILES,
    KEY_GENERATOR,
    KEY_ID,
    KEY_LAST_OPERATION,
    KEY_LOCK,
    KEY_MESSAGE,
    KEY_NAME,
    KEY_OUTPUT,
    KEY_PATH,
    KEY_PLANNED,
    KEY_PROFILE,
    KEY_PURGED,
    KEY_REMOVABLE,
    KEY_REPOSITORY,
    KEY_RESULTS,
    KEY_SCHEMA_VERSION,
    KEY_SHA256,
    KEY_SKIPPED,
    KEY_SOURCE,
    KEY_STATUS,
    KEY_SUMMARY,
    KEY_TARGET,
    KEY_TITLE,
    KEY_TYPE,
    KEY_UPDATED,
    KEY_VERSION,
    SEPARATOR_COMMA_SPACE,
    SEPARATOR_SPACE,
)

from . import __version__
from .adapters import is_generated_file, plan as plan_adapter
from .constants import (
    BASH, DEFAULT_COMMIT, ISO_TIMESPEC, STATE_DIR_NAME, TOOL_AST_GREP, TOOL_CODEGRAPH, TOOL_SERENA,
)
from .locking import (
    DEFAULT_ADAPTER,
    KEY_ADAPTER,
    KEY_ADAPTERS,
    KEY_COMPONENTS,
    KEY_DIGEST,
    KEY_PATH,
    KEY_PROFILE,
    KEY_SHA256,
    KEY_SOURCE,
    KEY_STATUS,
    PlannedFile,
    STATUS_MISSING,
    STATUS_MODIFIED,
    build_lock,
    lock_drift,
    merge_lock,
    planned_sha256,
    read_lock,
    set_adapter_digest,
    sha256_file,
    write_json,
)
from .paths import ToolWrightError, backup_root, is_within, lock_path, state_path
from .process import capture_command, git_commit, git_dirty, git_remote, run_command


TIMESTAMP_FORMAT = "%Y%m%dT%H%M%SZ"
DEFAULT_REPOSITORY = "https://github.com/GabrielAlmeidaFlores/ToolWright"

STATE_SCHEMA_VERSION = 1
BACKUP_SCRIPT = "scripts/maintenance/backup-config.sh"
ARCHIVE_GLOB = "*.tar.gz"

COMPONENT_TOOLS = frozenset({TOOL_AST_GREP, TOOL_SERENA, TOOL_CODEGRAPH})
RESULT_MESSAGE_CURRENT = "already up to date"

FLAG_PROJECT_ONLY = "--project-only"
COLON_NEWLINE = ":\n"




DEST_OPENCODE = ".opencode"
DEST_RALPH = ".ralph"

MESSAGE_MISSING_DESTINATIONS = "installer did not create "
MESSAGE_PLANNED_FILES = " planned file(s): "
MESSAGE_INSTALLER_FAILED = "installer failed with exit "
MESSAGE_BACKUP_SCRIPT_MISSING = "backup script not found: "
MESSAGE_LOCK_ESCAPES = "lock entry escapes the target: "
MESSAGE_NO_LOCK = "no lock file found at "
MESSAGE_NOTHING_TO_UNINSTALL = "; nothing to uninstall"


def plan_files(
    root: Path,
    target: Path,
    components: list[str],
    adapter: str = DEFAULT_ADAPTER,
) -> list[PlannedFile]:
    return plan_adapter(adapter, root, target, components)


def summarize_file_changes(planned: list[PlannedFile], target: Path) -> dict[str, int]:
    summary = {STATUS_NEW: 0, STATUS_UPDATED: 0, STATUS_UNCHANGED: 0}
    for item in planned:
        if not item.destination.is_file():
            summary[STATUS_NEW] += 1
        elif sha256_file(item.destination) == planned_sha256(item):
            summary[STATUS_UNCHANGED] += 1
        else:
            summary[STATUS_UPDATED] += 1
    return summary


def source_metadata(root: Path) -> dict[str, str]:
    return {
        KEY_REPOSITORY: git_remote(root) or DEFAULT_REPOSITORY,
        KEY_COMMIT: git_commit(root) or DEFAULT_COMMIT,
        KEY_VERSION: __version__,
        KEY_DIRTY: TRUE_VALUE if git_dirty(root) else FALSE_VALUE,
    }


def source_digest(planned: list[PlannedFile], target: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(planned, key=lambda entry: entry.destination.relative_to(target).as_posix()):
        relative = item.destination.relative_to(target).as_posix()
        digest.update(relative.encode(ENCODING_UTF8))
        digest.update(b"\0")
        digest.update(planned_sha256(item).encode(ASCII))
        digest.update(NEWLINE.encode(ASCII))
    return digest.hexdigest()


def installation_is_current(
    lock: dict[str, Any] | None,
    target: Path,
    profile: str,
    components: list[str],
    planned: list[PlannedFile],
    adapter: str = DEFAULT_ADAPTER,
) -> bool:
    if not lock:
        return False
    entry = next(
        (item for item in lock.get(KEY_ADAPTERS, []) if item.get(KEY_NAME) == adapter),
        None,
    )
    if entry is None:
        return False
    if entry.get(KEY_PROFILE) != profile or entry.get(KEY_COMPONENTS) != components:
        return False
    source = lock.get(KEY_SOURCE, {})
    expected = entry.get(KEY_DIGEST) or source.get(KEY_DIGEST)
    if expected != source_digest(planned, target):
        return False
    return not lock_drift(lock, target)


def archive_project_config(root: Path, target: Path, stamp: str) -> Path | None:
    if not (target / DEST_OPENCODE).exists() and not (target / DEST_RALPH).exists():
        return None
    destination = backup_root(target) / stamp
    script = root / BACKUP_SCRIPT
    if not script.is_file():
        raise ToolWrightError(f"{MESSAGE_BACKUP_SCRIPT_MISSING}{script}")
    run_command([BASH, str(script), FLAG_PROJECT_ONLY, str(destination)], cwd=target)
    return destination


def write_operation_state(target: Path, payload: dict[str, Any]) -> None:
    write_json(state_path(target), payload)


def apply_planned(planned: list[PlannedFile]) -> None:
    for item in planned:
        item.destination.parent.mkdir(parents=True, exist_ok=True)
        if item.content is not None:
            item.destination.write_text(item.content, encoding=ENCODING_UTF8)
        else:
            shutil.copy2(item.source, item.destination)


def backup_planned(planned: list[PlannedFile], target: Path, stamp: str) -> Path | None:
    existing = [item for item in planned if item.destination.is_file()]
    if not existing:
        return None
    destination = backup_root(target) / stamp / BACKUP_FILES_DIR
    for item in existing:
        relative = item.destination.relative_to(target)
        copy = destination / relative
        copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item.destination, copy)
    return destination


def run_shell_installer(root: Path, target: Path, components: list[str], apply: bool, clean: bool) -> str:
    script = root / INSTALL_SCRIPT
    command = [
        BASH,
        str(script),
        FLAG_APPLY if apply else FLAG_DRY_RUN,
        FLAG_ONLY,
        SEPARATOR_COMMA.join(components),
        FLAG_TARGET,
        str(target),
    ]
    if clean:
        command.append(FLAG_CLEAN)
    code, stdout, stderr = capture_command(command, cwd=root)
    if code != 0:
        raise ToolWrightError(f"{MESSAGE_INSTALLER_FAILED}{code}{COLON_NEWLINE}{stdout}{NEWLINE}{stderr}")
    return NEWLINE.join(part for part in (stdout, stderr) if part)


def install(
    root: Path,
    target: Path,
    profile: str,
    components: list[str],
    apply: bool,
    force: bool = False,
    clean: bool = False,
    adapter: str = DEFAULT_ADAPTER,
) -> dict[str, Any]:
    planned = plan_files(root, target, components, adapter=adapter)
    summary = summarize_file_changes(planned, target)
    existing_lock = read_lock(lock_path(target))
    current = installation_is_current(existing_lock, target, profile, components, planned, adapter=adapter)

    result: dict[str, Any] = {
        KEY_TARGET: str(target),
        KEY_ADAPTER: adapter,
        KEY_PROFILE: profile,
        KEY_COMPONENTS: components,
        KEY_PLANNED: [item.destination.relative_to(target).as_posix() for item in planned],
        KEY_SUMMARY: summary,
        KEY_CURRENT: current,
        KEY_APPLIED: False,
    }

    if not apply:
        result[KEY_OUTPUT] = (
            run_shell_installer(root, target, components, apply=False, clean=clean)
            if adapter == DEFAULT_ADAPTER
            else MESSAGE_GENERATED_PLAN
        )
        return result

    if current and not force:
        if existing_lock is not None:
            existing_lock[KEY_SOURCE] = source_metadata(root)
            digest = source_digest(planned, target)
            existing_lock[KEY_SOURCE][KEY_DIGEST] = digest
            set_adapter_digest(existing_lock, adapter, digest)
            write_json(lock_path(target), existing_lock)
        result[KEY_MESSAGE] = RESULT_MESSAGE_CURRENT
        return result

    target.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime(TIMESTAMP_FORMAT)
    backup = archive_project_config(root, target, stamp) if adapter == DEFAULT_ADAPTER else backup_planned(planned, target, stamp)
    result[KEY_BACKUP] = str(backup) if backup else None

    if adapter == DEFAULT_ADAPTER:
        result[KEY_OUTPUT] = run_shell_installer(root, target, components, apply=True, clean=clean)
    else:
        apply_planned(planned)
        result[KEY_OUTPUT] = MESSAGE_GENERATED_FILES

    missing = [item.destination for item in planned if not item.destination.is_file()]
    if missing:
        raise ToolWrightError(f"{MESSAGE_MISSING_DESTINATIONS}{len(missing)}{MESSAGE_PLANNED_FILES}{missing[0]}")

    lock = build_lock(root, target, profile, components, planned, source_metadata(root), adapter=adapter)
    if existing_lock is not None:
        lock = merge_lock(existing_lock, lock)
    digest = source_digest(planned, target)
    set_adapter_digest(lock, adapter, digest)
    lock[KEY_SOURCE][KEY_DIGEST] = digest
    write_json(lock_path(target), lock)
    write_operation_state(
        target,
        {
            KEY_SCHEMA_VERSION: STATE_SCHEMA_VERSION,
            KEY_UPDATED: datetime.now(timezone.utc).isoformat(timespec=ISO_TIMESPEC),
            KEY_LAST_OPERATION: OPERATION_INSTALL,
            KEY_TARGET: str(target),
            KEY_PROFILE: profile,
            KEY_COMPONENTS: components,
            KEY_BACKUP: str(backup) if backup else None,
        },
    )
    result[KEY_APPLIED] = True
    result[KEY_LOCK] = str(lock_path(target))
    return result


def uninstall(
    target: Path,
    apply: bool,
    force: bool = False,
    purge: bool = False,
) -> dict[str, Any]:
    lock = read_lock(lock_path(target))
    if lock is None:
        raise ToolWrightError(f"{MESSAGE_NO_LOCK}{lock_path(target)}{MESSAGE_NOTHING_TO_UNINSTALL}")

    removable: list[str] = []
    seen: set[str] = set()
    skipped: list[dict[str, str]] = []
    for entry in lock.get(KEY_FILES, []):
        relative = entry.get(KEY_PATH, EMPTY_STRING)
        path = target / relative
        if not is_within(path, target):
            raise ToolWrightError(f"{MESSAGE_LOCK_ESCAPES}{relative}")
        if not path.is_file():
            continue
        if not force and sha256_file(path) != entry.get(KEY_SHA256):
            skipped.append({KEY_PATH: relative, KEY_STATUS: STATUS_MODIFIED})
            continue
        if relative not in seen:
            seen.add(relative)
            removable.append(relative)

    result: dict[str, Any] = {
        KEY_TARGET: str(target),
        KEY_REMOVABLE: removable,
        KEY_SKIPPED: skipped,
        KEY_APPLIED: False,
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
        shutil.rmtree(target / STATE_DIR_NAME, ignore_errors=True)
        lock_path(target).unlink(missing_ok=True)
        result[KEY_PURGED] = True
    else:
        remaining = [
            entry
            for entry in lock.get(KEY_FILES, [])
            if entry.get(KEY_PATH) not in seen
            and (target / entry.get(KEY_PATH, EMPTY_STRING)).is_file()
        ]
        remaining_adapters = {entry.get(KEY_ADAPTER) for entry in remaining}
        lock[KEY_FILES] = remaining
        lock[KEY_ADAPTERS] = [
            entry
            for entry in lock.get(KEY_ADAPTERS, [])
            if entry.get(KEY_NAME) in remaining_adapters
        ]
        write_json(lock_path(target), lock)
        write_operation_state(
            target,
            {
                KEY_SCHEMA_VERSION: STATE_SCHEMA_VERSION,
                KEY_UPDATED: datetime.now(timezone.utc).isoformat(timespec=ISO_TIMESPEC),
                KEY_LAST_OPERATION: OPERATION_UNINSTALL,
                KEY_TARGET: str(target),
            },
        )
    result[KEY_APPLIED] = True
    return result


def list_backups(target: Path) -> list[dict[str, Any]]:
    root = backup_root(target)
    if not root.is_dir():
        return []
    backups: list[dict[str, Any]] = []
    for directory in sorted(root.iterdir(), reverse=True):
        if not directory.is_dir():
            continue
        archives = sorted(path.name for path in directory.glob(ARCHIVE_GLOB))
        backups.append({KEY_PATH: str(directory), KEY_ARCHIVES: archives})
    return backups


def read_state(target: Path) -> dict[str, Any] | None:
    path = state_path(target)
    if not path.is_file():
        return None
    with path.open(encoding=ENCODING_UTF8) as handle:
        data = json.load(handle)
    return data if isinstance(data, dict) else None
