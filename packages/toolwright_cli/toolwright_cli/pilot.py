"""
Real-repository pilot runner for ``toolwright pilot``.

Public API: :func:`load_pilots`, :func:`list_pilots`, and :func:`run_pilot`.

A real pilot runs in a disposable clone under a workspace directory. The
repository is cloned at a pinned commit, the profile is installed into that
clone, one prompt is executed with a configured model, and a verification
command records correctness. Artifacts stay in the workspace; the clone is
removed unless ``keep`` is true.

Side effects: network access (git clone), writes under the workspace, and one
model invocation. It never stages or commits in the user's repository and never
runs Ralph.
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import time
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import stats
from .installer import install
from .paths import ToolwrightError
from .process import capture_command
from .profiles import load_profiles, resolve_components

CONFIG = Path("configs/pilots/pilots.toml")
REQUIRED = ("repository", "commit", "stack", "focus")


def load_pilots(root: Path) -> dict[str, dict[str, str]]:
    path = root / CONFIG
    if not path.is_file():
        raise ToolwrightError(f"pilot configuration not found: {path}")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as error:
        raise ToolwrightError(f"{path}: invalid TOML: {error}") from error
    pilots = data.get("pilots")
    if not isinstance(pilots, dict) or not pilots:
        raise ToolwrightError(f"{path}: missing [pilots.<name>] tables")
    results: dict[str, dict[str, str]] = {}
    for name, entry in pilots.items():
        if not isinstance(entry, dict):
            raise ToolwrightError(f"{path}: pilots.{name} must be a table")
        missing = [field for field in REQUIRED if not str(entry.get(field, "")).strip()]
        if missing:
            raise ToolwrightError(f"{path}: pilots.{name} missing {', '.join(missing)}")
        results[name] = {field: str(entry[field]) for field in REQUIRED}
    return results


def list_pilots(root: Path) -> list[dict[str, str]]:
    pilots = load_pilots(root)
    return [{"name": name, **entry} for name, entry in sorted(pilots.items())]


def require_pilot_argument(value: str | None, label: str) -> str:
    if not value or not value.strip():
        raise ToolwrightError(f"{label} is required for a real pilot run")
    return value.strip()


def run_git(args: list[str], cwd: Path | None = None, timeout: int = 1800) -> None:
    code, stdout, stderr = capture_command(["git", *args], cwd=cwd, timeout=timeout)
    if code != 0:
        raise ToolwrightError(f"git {' '.join(args)} failed: {stderr or stdout}")


def run_pilot(
    root: Path,
    name: str,
    workspace: Path | None,
    prompt: str | None,
    verify_command: str | None,
    profile: str,
    keep: bool,
    dry_run: bool,
    model: str | None,
    agent: str = "coordinator",
    setup_command: str | None = None,
) -> dict[str, Any]:
    pilots = load_pilots(root)
    if name not in pilots:
        raise ToolwrightError(f"unknown pilot: {name} (available: {', '.join(sorted(pilots))})")
    pilot = pilots[name]
    profiles = load_profiles(root)
    components = resolve_components(profiles, profile, None)
    directory = workspace or Path(tempfile.mkdtemp(prefix=f"toolwright-pilot-{name}-"))
    clone = directory / "clone"
    artifacts = directory / "artifacts"
    commands = [
        f"git clone --no-checkout --filter=blob:none {pilot['repository']} {clone}",
        f"git -C {clone} fetch --depth 1 origin {pilot['commit']}",
        f"git -C {clone} checkout --detach FETCH_HEAD",
        f"toolwright install --profile {profile} --target {clone} --apply",
        f"bash -lc {setup_command or '<setup command>'}",
        f"opencode --standalone run --agent {agent} --model {model or '<provider/model>'} --auto --format json <prompt>",
        f"bash -lc {verify_command or '<verification command>'}",
    ]
    if dry_run:
        return {
            "pilot": name,
            "repository": pilot["repository"],
            "commit": pilot["commit"],
            "workspace": str(directory),
            "profile": profile,
            "components": components,
            "steps": commands,
            "dry_run": True,
        }

    prompt_value = require_pilot_argument(prompt, "prompt")
    verify_value = require_pilot_argument(verify_command, "verification command")
    model_value = require_pilot_argument(model, "OPENCODE_PILOT_MODEL")
    directory.mkdir(parents=True, exist_ok=True)
    artifacts.mkdir(parents=True, exist_ok=True)
    if clone.exists():
        raise ToolwrightError(f"workspace already contains a clone: {clone}")

    started = time.monotonic()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        run_git(["clone", "--no-checkout", "--filter=blob:none", pilot["repository"], str(clone)])
        run_git(["-C", str(clone), "fetch", "--depth", "1", "origin", pilot["commit"]])
        run_git(["-C", str(clone), "checkout", "--detach", "FETCH_HEAD"])
        install(root=root, target=clone, profile=profile, components=components, apply=True)
        if setup_command:
            setup_code, setup_out, setup_err = capture_command(
                ["bash", "-lc", setup_command],
                cwd=clone,
                timeout=1800,
            )
            if setup_code != 0:
                raise ToolwrightError(f"pilot setup failed: {setup_err or setup_out}")
        environment = dict(os.environ)
        environment["PWD"] = str(clone)
        environment["OPENCODE_CONFIG"] = str(clone / ".opencode/opencode.jsonc")
        code, session, session_error = capture_command(
            [
                "opencode",
                "--standalone",
                "run",
                "--agent",
                agent,
                "--model",
                model_value,
                "--auto",
                "--format",
                "json",
                prompt_value,
            ],
            cwd=clone,
            env=environment,
            timeout=3600,
        )
        (artifacts / "session.jsonl").write_text(session, encoding="utf-8")
        verify_code, verify_out, verify_err = capture_command(["bash", "-lc", verify_value], cwd=clone, timeout=3600)
        (artifacts / "verification.log").write_text(
            f"command: {verify_value}\nexit: {verify_code}\n\n{verify_out}\n{verify_err}\n",
            encoding="utf-8",
        )
        session_totals = stats.parse_session(artifacts / "session.jsonl")
        result = {
            "pilot": name,
            "repository": pilot["repository"],
            "commit": pilot["commit"],
            "profile": profile,
            "components": components,
            "model": model_value,
            "agent": agent,
            "prompt": prompt_value,
            "verification_command": verify_value,
            "verification_exit": verify_code,
            "opencode_exit": code,
            "setup_command": setup_command,
            "success": verify_code == 0 and code == 0,
            "opencode_stderr": session_error,
            "started_at": started_at,
            "finished_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "wall_time_seconds": round(time.monotonic() - started, 2),
            "cost": session_totals["cost"],
            "input_tokens": session_totals["input_tokens"],
            "output_tokens": session_totals["output_tokens"],
            "tool_calls": session_totals["tool_calls"],
            "tool_errors": session_totals["tool_errors"],
            "workspace": str(directory),
            "dry_run": False,
        }
        (artifacts / "meta.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (artifacts / "summary.md").write_text(
            "# Pilot Run\n\n"
            f"- Pilot: {name}\n"
            f"- Repository: {pilot['repository']}\n"
            f"- Commit: {pilot['commit']}\n"
            f"- Model: {model_value}\n"
            f"- OpenCode exit: {code}\n"
            f"- Success: {verify_code == 0 and code == 0}\n"
            f"- Verification exit: {verify_code}\n"
            f"- Cost: ${session_totals['cost']:.6f}\n"
            f"- Tokens: {session_totals['input_tokens']} input, {session_totals['output_tokens']} output\n"
            f"- Tool calls: {session_totals['tool_calls']} ({session_totals['tool_errors']} errors)\n"
            f"- Wall time: {result['wall_time_seconds']}s\n\n"
            "Success requires both the OpenCode run and the verification command to exit zero. "
            "Rework and human intervention must be recorded separately.\n",
            encoding="utf-8",
        )
        return result
    finally:
        if clone.exists() and not keep:
            shutil.rmtree(clone, ignore_errors=True)
