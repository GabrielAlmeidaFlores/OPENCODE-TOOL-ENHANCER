"""
Environment and repository diagnostics for ``ote doctor``.

Public API: :class:`Check`, :func:`run_diagnostic_checks`, and :func:`summarize_checks`.

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
from .process import capture_command

MIN_PYTHON = (3, 11)


@dataclass(frozen=True)
class Check:

    id: str
    status: str
    detail: str


def build_check_result(identifier: str, status: str, detail: str) -> Check:
    return Check(id=identifier, status=status, detail=detail)


def check_python_version() -> Check:
    current = sys.version_info
    version = f"{current.major}.{current.minor}.{current.micro}"
    if (current.major, current.minor) < MIN_PYTHON:
        return build_check_result("python", "fail", f"{version} is older than 3.11")
    return build_check_result("python", "ok", version)


def check_command_available(name: str, required: bool) -> Check:
    location = shutil.which(name)
    if location:
        return build_check_result(name, "ok", location)
    return build_check_result(name, "fail" if required else "warn", "not found on PATH")


def check_repository_layout(root: Path) -> Check:
    required = [
        "VERSION",
        "configs/opencode/opencode.jsonc",
        "agents/coordinator/AGENT.md",
        "scripts/installation/install.sh",
        "docs/provenance/registry.yml",
    ]
    missing = [item for item in required if not (root / item).exists()]
    if missing:
        return build_check_result("repository", "fail", f"missing: {', '.join(missing)}")
    return build_check_result("repository", "ok", str(root))


def check_artifact_counts(root: Path) -> Check:
    agents = len(list((root / "agents").glob("*/AGENT.md")))
    commands = len(list((root / "commands").glob("*.md")))
    skills = len(list((root / "skills").glob("*/SKILL.md")))
    hats = len(list((root / "configs/ralph/hats").glob("*.yml")))
    if min(agents, commands, skills, hats) == 0:
        return build_check_result("artifacts", "fail", f"agents={agents} commands={commands} skills={skills} hats={hats}")
    return build_check_result(
        "artifacts",
        "ok",
        f"{agents} agents, {commands} commands, {skills} skills, {hats} hats",
    )


def check_opencode_version() -> Check:
    code, stdout, stderr = capture_command(["opencode", "--version"])
    if code != 0:
        return build_check_result("opencode", "fail", stderr or "opencode --version failed")
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", stdout)
    if match is None:
        return build_check_result("opencode", "warn", stdout)
    major = int(match.group(1))
    if major < 2:
        return build_check_result("opencode", "fail", f"{stdout} is V1; this profile requires V2")
    return build_check_result("opencode", "ok", stdout)


def run_repository_validator(root: Path) -> Check:
    script = root / "scripts/validation/validate_config.py"
    if not script.is_file():
        return build_check_result("validator", "fail", f"missing {script}")
    code, stdout, stderr = capture_command([sys.executable, str(script)])
    if code != 0:
        lines = [line for line in (stdout + "\n" + stderr).splitlines() if line.startswith("ERROR")]
        detail = lines[0] if lines else "validator failed"
        return build_check_result("validator", "fail", detail)
    count = re.search(r"checked: (\d+)", stdout)
    return build_check_result("validator", "ok", f"checked: {count.group(1)}" if count else "ok")


def check_mcp_connections(target: Path) -> Check:
    config = target / ".opencode/opencode.jsonc"
    if not config.is_file():
        return build_check_result("mcp", "warn", "no .opencode/opencode.jsonc in the target; skipping")
    environment = dict(os.environ)
    environment["OPENCODE_CONFIG"] = str(config)
    code, stdout, stderr = capture_command(["opencode", "--standalone", "mcp", "list"], cwd=target, env=environment)
    if code != 0:
        return build_check_result("mcp", "fail", (stderr or stdout or "mcp list failed").splitlines()[0])
    lines = [line for line in stdout.splitlines() if line.strip()]
    return build_check_result("mcp", "ok", f"{len(lines)} line(s) reported")


def check_installation_lock(target: Path) -> Check:
    path = lock_path(target)
    if not path.is_file():
        return build_check_result("lock", "warn", "no ote.lock.json in the target; nothing installed by ote yet")
    try:
        lock = read_lock(path)
    except (ValueError, OSError) as error:
        return build_check_result("lock", "fail", str(error))
    drift = lock_drift(lock or {}, target)
    if drift:
        first = drift[0]
        return build_check_result("lock", "fail", f"{len(drift)} file(s) differ, e.g. {first['path']} ({first['status']})")
    return build_check_result("lock", "ok", f"{len(lock.get('files', []))} managed file(s) match")


def check_cli_state(target: Path) -> Check:
    directory = state_path(target).parent
    if not directory.exists():
        return build_check_result("state", "warn", "no .ote/state.json yet")
    if not directory.is_dir():
        return build_check_result("state", "fail", f"{directory} is not a directory")
    return build_check_result("state", "ok", str(directory))


def run_diagnostic_checks(root: Path, target: Path, mcp: bool = True) -> list[Check]:
    checks = [
        check_python_version(),
        check_repository_layout(root),
        check_artifact_counts(root),
        check_command_available("git", required=True),
        check_opencode_version(),
        check_command_available("node", required=False),
        check_command_available("rg", required=False),
        check_command_available("ast-grep", required=False),
        check_command_available("serena", required=False),
        check_command_available("codegraph", required=False),
        check_command_available("ralph", required=False),
        run_repository_validator(root),
        check_installation_lock(target),
        check_cli_state(target),
    ]
    if mcp:
        checks.append(check_mcp_connections(target))
    else:
        checks.append(build_check_result("mcp", "warn", "skipped by --no-mcp"))
    return checks


def summarize_checks(checks: list[Check]) -> dict[str, int]:
    summary = {"ok": 0, "warn": 0, "fail": 0}
    for check in checks:
        summary[check.status] = summary.get(check.status, 0) + 1
    return summary


def checks_as_dict(checks: list[Check]) -> dict[str, Any]:
    return {
        "checks": [{"id": check.id, "status": check.status, "detail": check.detail} for check in checks],
        "summary": summarize_checks(checks),
    }
