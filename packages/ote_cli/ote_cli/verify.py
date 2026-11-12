"""
Deterministic verification engine for ``ote verify``.

Public API: :class:`Check`, :class:`Result`, :func:`load_config`,
:func:`run_checks`, and :func:`failure_class`.

Configuration: ``.ote/config.toml`` with a ``[verify]`` table and one
``[verify.checks.<name>]`` table per check. TOML is used because Python 3.11
provides a standard-library parser, keeping the CLI dependency-free.

Side effects: executes the configured commands and writes cache entries under
``.ote/cache/verify`` when a check declares ``inputs``.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .paths import OteError

DEFAULT_TIMEOUT = 900
MAX_OUTPUT = 8000
CACHE_SCHEMA_VERSION = 1
NAME_PATTERN = r"^[a-z0-9][a-z0-9_-]*$"


@dataclass(frozen=True)
class Check:
    """
    One configured verification command.
    """

    name: str
    command: str
    timeout: float
    inputs: tuple[str, ...]


@dataclass(frozen=True)
class Result:
    """
    One verification result.
    """

    name: str
    status: str
    exit_code: int
    seconds: float
    failure_class: str
    stdout: str
    stderr: str
    cached: bool


def _validate_name(name: str) -> None:
    """
    Reject check names that are not filesystem- and CLI-safe.
    """
    if not re.match(NAME_PATTERN, name):
        raise OteError(f"invalid check name: {name}")


def load_config(root: Path, path: Path | None = None) -> tuple[dict[str, Check], dict[str, Any]]:
    """
    Load and validate the verification and governance configuration.
    """
    config_path = path or root / ".ote/config.toml"
    if not config_path.is_file():
        raise OteError(f"missing verification config: {config_path}")
    try:
        data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as error:
        raise OteError(f"{config_path}: invalid TOML: {error}") from error
    if not isinstance(data, dict):
        raise OteError(f"{config_path}: configuration must be a table")

    verify_section = data.get("verify")
    if not isinstance(verify_section, dict):
        raise OteError(f"{config_path}: missing [verify] table")
    default_timeout = verify_section.get("timeout", DEFAULT_TIMEOUT)
    if not isinstance(default_timeout, (int, float)) or default_timeout <= 0:
        raise OteError(f"{config_path}: verify.timeout must be a positive number")

    checks_section = verify_section.get("checks")
    if not isinstance(checks_section, dict) or not checks_section:
        raise OteError(f"{config_path}: missing [verify.checks.<name>] tables")

    checks: dict[str, Check] = {}
    for name, entry in checks_section.items():
        _validate_name(name)
        if not isinstance(entry, dict):
            raise OteError(f"{config_path}: verify.checks.{name} must be a table")
        command = entry.get("command")
        if not isinstance(command, str) or not command.strip():
            raise OteError(f"{config_path}: verify.checks.{name}.command is required")
        timeout = entry.get("timeout", default_timeout)
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise OteError(f"{config_path}: verify.checks.{name}.timeout must be positive")
        inputs = entry.get("inputs", [])
        if not isinstance(inputs, list) or not all(isinstance(item, str) for item in inputs):
            raise OteError(f"{config_path}: verify.checks.{name}.inputs must be a list of paths")
        for item in inputs:
            candidate = Path(item)
            if candidate.is_absolute() or ".." in candidate.parts:
                raise OteError(f"{config_path}: verify.checks.{name}.inputs must stay inside the repository")
        checks[name] = Check(name=name, command=command, timeout=float(timeout), inputs=tuple(inputs))

    governance = data.get("governance", {})
    if not isinstance(governance, dict):
        raise OteError(f"{config_path}: governance must be a table")
    mode = governance.get("validator_mode", "advisory")
    if mode not in {"off", "advisory", "strict"}:
        raise OteError(f"{config_path}: governance.validator_mode must be off, advisory, or strict")
    return checks, governance


def failure_class(name: str, exit_code: int, timed_out: bool) -> str:
    """
    Classify a failed check for reports and rework analysis.
    """
    if timed_out:
        return "timeout"
    if exit_code == 127:
        return "missing-command"
    if exit_code == 126:
        return "permission"
    lowered = name.lower()
    for token, label in (
        ("test", "test-failure"),
        ("lint", "lint-failure"),
        ("type", "type-failure"),
        ("validate", "validation-failure"),
        ("security", "security-failure"),
    ):
        if token in lowered:
            return label
    return "command-failure"


def _digest_paths(root: Path, inputs: tuple[str, ...]) -> str:
    """
    Return a digest over the declared input files and directories.
    """
    digest = hashlib.sha256()
    for relative in sorted(inputs):
        path = root / relative
        if not path.exists():
            raise OteError(f"cache input does not exist: {relative}")
        files = [path] if path.is_file() else sorted(item for item in path.rglob("*") if _is_input_file(item))
        for file in files:
            digest.update(file.relative_to(root).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(hashlib.sha256(file.read_bytes()).hexdigest().encode("ascii"))
            digest.update(b"\n")
    return digest.hexdigest()


def _is_input_file(path: Path) -> bool:
    """
    Exclude generated and operating-system files from input digests.
    """
    if not path.is_file():
        return False
    if path.name == ".DS_Store" or path.suffix in {".pyc", ".pyo"}:
        return False
    return not any(part in {"__pycache__", ".egg-info", "node_modules"} or part.endswith(".egg-info") for part in path.parts)


def cache_key(check: Check, root: Path) -> str:
    """
    Return a deterministic cache key for one check.
    """
    digest = hashlib.sha256()
    digest.update(check.name.encode("utf-8"))
    digest.update(b"\0")
    digest.update(check.command.encode("utf-8"))
    digest.update(b"\0")
    digest.update(check.timeout.__repr__().encode("ascii"))
    digest.update(b"\0")
    digest.update(sys.version.encode("utf-8"))
    if check.inputs:
        digest.update(b"\0")
        digest.update(_digest_paths(root, check.inputs).encode("ascii"))
    return digest.hexdigest()


def _truncate(value: str) -> str:
    """
    Bound captured output so cache files and reports stay small.
    """
    return value if len(value) <= MAX_OUTPUT else value[-MAX_OUTPUT:]


def _read_cache(path: Path, key: str, name: str) -> Result | None:
    """
    Read a cached result when it matches the current key.
    """
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    if data.get("schema_version") != CACHE_SCHEMA_VERSION or data.get("key") != key:
        return None
    if data.get("status") != "pass":
        return None
    try:
        return Result(
            name=name,
            status=str(data.get("status", "fail")),
            exit_code=int(data.get("exit_code", 1)),
            seconds=float(data.get("seconds", 0)),
            failure_class=str(data.get("failure_class", "command-failure")),
            stdout=str(data.get("stdout", "")),
            stderr=str(data.get("stderr", "")),
            cached=True,
        )
    except (TypeError, ValueError):
        return None


def _write_cache(path: Path, key: str, result: Result) -> None:
    """
    Persist a successful or failed result for the current key.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": CACHE_SCHEMA_VERSION,
        "key": key,
        "status": result.status,
        "exit_code": result.exit_code,
        "seconds": result.seconds,
        "failure_class": result.failure_class,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _execute(root: Path, check: Check) -> Result:
    """
    Run one check and return its result.
    """
    started = time.monotonic()
    try:
        process = subprocess.run(
            check.command,
            cwd=str(root),
            shell=True,
            capture_output=True,
            text=True,
            timeout=check.timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout.decode() if isinstance(error.stdout, bytes) else (error.stdout or "")
        stderr = error.stderr.decode() if isinstance(error.stderr, bytes) else (error.stderr or "")
        return Result(
            name=check.name,
            status="fail",
            exit_code=124,
            seconds=round(time.monotonic() - started, 2),
            failure_class="timeout",
            stdout=_truncate(stdout),
            stderr=_truncate(stderr or f"timed out after {check.timeout}s"),
            cached=False,
        )
    seconds = round(time.monotonic() - started, 2)
    exit_code = process.returncode
    return Result(
        name=check.name,
        status="pass" if exit_code == 0 else "fail",
        exit_code=exit_code,
        seconds=seconds,
        failure_class="" if exit_code == 0 else failure_class(check.name, exit_code, False),
        stdout=_truncate(process.stdout),
        stderr=_truncate(process.stderr),
        cached=False,
    )


def run_checks(
    root: Path,
    checks: dict[str, Check],
    only: list[str] | None = None,
    use_cache: bool = True,
    cache_dir: Path | None = None,
) -> list[Result]:
    """
    Run the selected checks in configuration order and return their results.
    """
    selected = list(only) if only else list(checks)
    unknown = [name for name in selected if name not in checks]
    if unknown:
        raise OteError(f"unknown checks: {', '.join(unknown)}")
    directory = cache_dir or root / ".ote/cache/verify"
    results: list[Result] = []
    for name in selected:
        check = checks[name]
        key = cache_key(check, root)
        cached: Result | None = None
        if use_cache and check.inputs:
            cached = _read_cache(directory / f"{name}.json", key, name)
        if cached is not None:
            results.append(cached)
            continue
        result = _execute(root, check)
        if use_cache and check.inputs and result.status == "pass":
            _write_cache(directory / f"{name}.json", key, result)
        results.append(result)
    return results


def summarize(results: list[Result]) -> dict[str, Any]:
    """
    Return counts and the overall status for a set of results.
    """
    failures = [result for result in results if result.status == "fail"]
    return {
        "total": len(results),
        "passed": len(results) - len(failures),
        "failed": len(failures),
        "status": "fail" if failures else "pass",
        "failure_classes": sorted({result.failure_class for result in failures if result.failure_class}),
    }
