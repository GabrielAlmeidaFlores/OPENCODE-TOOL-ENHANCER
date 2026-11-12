"""
Environment and repository diagnostics for ``ote doctor``.

Public API: :class:`Check`, :func:`run_checks`, and :func:`summarize`.

Side effects: executes read-only commands such as ``opencode debug`` and the
repository validator. It never writes files.

Module constants: ``MIN_PYTHON`` is the oldest supported interpreter.
"""
from __future__ import annotations

import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .locking import lock_drift, read_lock
from .paths import lock_path, state_path
from .process import capture

MIN_PYTHON = (3, 11)


@dataclass(frozen=True)
class Check:
    """
    One diagnostic result.
    """

    id: str
    status: str
    detail: str


def _result(identifier: str, status: str, detail: str) -> Check:
    """
    Build a check result.
    """
    return Check(id=identifier, status=status, detail=detail)


def _check_python() -> Check:
    """
    Check the interpreter version.
    """
    current = sys.version_info
    version = f"{current.major}.{current.minor}.{current.micro}"
    if (current.major, current.minor) < MIN_PYTHON:
        return _result("python", "fail", f"{version} is older than 3.11")
    return _result("python", "ok", version)


def _check_binary(name: str, required: bool) -> Check:
    """
    Check whether a command is available on PATH.
    """
    location = shutil.which(name)
    if location:
        return _result(name, "ok", location)
    return _result(name, "fail" if required else "warn", "not found on PATH")


def _check_required_paths(root: Path) -> Check:
    """
    Check the repository layout expected by the CLI.
    """
    required = [
        "VERSION",
        "configs/opencode/opencode.jsonc",
        "agents/coordinator/AGENT.md",
        "scripts/installation/install.sh",
        "docs/provenance/registry.yml",
    ]
    missing = [item for item in required if not (root / item).exists()]
    if missing:
        return _result("repository", "fail", f"missing: {', '.join(missing)}")
    return _result("repository", "ok", str(root))


def _check_counts(root: Path) -> Check:
    """
    Check that artifacts are present and countable.
    """
    agents = len(list((root / "agents").glob("*/AGENT.md")))
    commands = len(list((root / "commands").glob("*.md")))
    skills = len(list((root / "skills").glob("*/SKILL.md")))
    hats = len(list((root / "configs/ralph/hats").glob("*.yml")))
    if min(agents, commands, skills, hats) == 0:
        return _result("artifacts", "fail", f"agents={agents} commands={commands} skills={skills} hats={hats}")
    return _result(
        "artifacts",
        "ok",
        f"{agents} agents, {commands} commands, {skills} skills, {hats} hats",
    )


def _check_opencode() -> Check:
    """
    Check that OpenCode V2 is installed.
    """
    code, stdout, stderr = capture(["opencode", "--version"])
    if code != 0:
        return _result("opencode", "fail", stderr or "opencode --version failed")
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", stdout)
    if match is None:
        return _result("opencode", "warn", stdout)
    major = int(match.group(1))
    if major < 2:
        return _result("opencode", "fail", f"{stdout} is V1; this profile requires V2")
    return _result("opencode", "ok", stdout)


def _check_validator(root: Path) -> Check:
    """
    Run the repository validator and summarize its result.
    """
    script = root / "scripts/validation/validate_config.py"
    if not script.is_file():
        return _result("validator", "fail", f"missing {script}")
    code, stdout, stderr = capture([sys.executable, str(script)])
    if code != 0:
        lines = [line for line in (stdout + "\n" + stderr).splitlines() if line.startswith("ERROR")]
        detail = lines[0] if lines else "validator failed"
        return _result("validator", "fail", detail)
    count = re.search(r"checked: (\d+)", stdout)
    return _result("validator", "ok", f"checked: {count.group(1)}" if count else "ok")


def _check_mcp(target: Path) -> Check:
    """
    Query configured MCP servers for the target project.
    """
    config = target / ".opencode/opencode.jsonc"
    if not config.is_file():
        return _result("mcp", "warn", "no .opencode/opencode.jsonc in the target; skipping")
    environment = dict(os.environ)
    environment["OPENCODE_CONFIG"] = str(config)
    code, stdout, stderr = capture(["opencode", "--standalone", "mcp", "list"], cwd=target, env=environment)
    if code != 0:
        return _result("mcp", "fail", (stderr or stdout or "mcp list failed").splitlines()[0])
    lines = [line for line in stdout.splitlines() if line.strip()]
    return _result("mcp", "ok", f"{len(lines)} line(s) reported")


def _check_lock(target: Path) -> Check:
    """
    Check managed files against the installation lock.
    """
    path = lock_path(target)
    if not path.is_file():
        return _result("lock", "warn", "no ote.lock.json in the target; nothing installed by ote yet")
    try:
        lock = read_lock(path)
    except (ValueError, OSError) as error:
        return _result("lock", "fail", str(error))
    drift = lock_drift(lock or {}, target)
    if drift:
        first = drift[0]
        return _result("lock", "fail", f"{len(drift)} file(s) differ, e.g. {first['path']} ({first['status']})")
    return _result("lock", "ok", f"{len(lock.get('files', []))} managed file(s) match")


def _check_state(target: Path) -> Check:
    """
    Check that the state directory is writable when it already exists.
    """
    directory = state_path(target).parent
    if not directory.exists():
        return _result("state", "warn", "no .ote/state.json yet")
    if not directory.is_dir():
        return _result("state", "fail", f"{directory} is not a directory")
    return _result("state", "ok", str(directory))


def run_checks(root: Path, target: Path, mcp: bool = True) -> list[Check]:
    """
    Run every diagnostic check in a stable order.
    """
    checks = [
        _check_python(),
        _check_required_paths(root),
        _check_counts(root),
        _check_binary("git", required=True),
        _check_opencode(),
        _check_binary("node", required=False),
        _check_binary("rg", required=False),
        _check_binary("ast-grep", required=False),
        _check_binary("serena", required=False),
        _check_binary("codegraph", required=False),
        _check_binary("ralph", required=False),
        _check_validator(root),
        _check_lock(target),
        _check_state(target),
    ]
    if mcp:
        checks.append(_check_mcp(target))
    else:
        checks.append(_result("mcp", "warn", "skipped by --no-mcp"))
    return checks


def summarize(checks: list[Check]) -> dict[str, int]:
    """
    Count checks by status.
    """
    summary = {"ok": 0, "warn": 0, "fail": 0}
    for check in checks:
        summary[check.status] = summary.get(check.status, 0) + 1
    return summary


def as_dict(checks: list[Check]) -> dict[str, Any]:
    """
    Return the JSON-serializable representation used by ``--json``.
    """
    return {
        "checks": [{"id": check.id, "status": check.status, "detail": check.detail} for check in checks],
        "summary": summarize(checks),
    }
