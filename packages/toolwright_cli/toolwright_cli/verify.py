"""
Deterministic verification engine for ``toolwright verify``.

Public API: :class:`Check`, :class:`Result`, :func:`load_verification_config`,
:func:`run_verification_checks`, and :func:`classify_failure`.

Configuration: ``.toolwright/config.toml`` with a ``[verify]`` table and one
``[verify.checks.<name>]`` table per check. TOML is used because Python 3.11
provides a standard-library parser, keeping the CLI dependency-free.

Side effects: executes the configured commands and writes cache entries under
``.toolwright/cache/verify`` when a check declares ``inputs``.
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

from .paths import ToolwrightError

DEFAULT_TIMEOUT = 900
MAX_OUTPUT = 8000
CACHE_SCHEMA_VERSION = 1
NAME_PATTERN = r"^[a-z0-9][a-z0-9_-]*$"


@dataclass(frozen=True)
class Check:

    name: str
    command: str
    timeout: float
    inputs: tuple[str, ...]


@dataclass(frozen=True)
class Result:

    name: str
    status: str
    exit_code: int
    seconds: float
    failure_class: str
    stdout: str
    stderr: str
    cached: bool


def validate_check_name(name: str) -> None:
    if not re.match(NAME_PATTERN, name):
        raise ToolwrightError(f"invalid check name: {name}")


def load_verification_config(root: Path, path: Path | None = None) -> tuple[dict[str, Check], dict[str, Any]]:
    config_path = path or root / ".toolwright/config.toml"
    if not config_path.is_file():
        raise ToolwrightError(f"missing verification config: {config_path}")
    try:
        data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as error:
        raise ToolwrightError(f"{config_path}: invalid TOML: {error}") from error
    if not isinstance(data, dict):
        raise ToolwrightError(f"{config_path}: configuration must be a table")

    verify_section = data.get("verify")
    if not isinstance(verify_section, dict):
        raise ToolwrightError(f"{config_path}: missing [verify] table")
    default_timeout = verify_section.get("timeout", DEFAULT_TIMEOUT)
    if not isinstance(default_timeout, (int, float)) or default_timeout <= 0:
        raise ToolwrightError(f"{config_path}: verify.timeout must be a positive number")

    checks_section = verify_section.get("checks")
    if not isinstance(checks_section, dict) or not checks_section:
        raise ToolwrightError(f"{config_path}: missing [verify.checks.<name>] tables")

    checks: dict[str, Check] = {}
    for name, entry in checks_section.items():
        validate_check_name(name)
        if not isinstance(entry, dict):
            raise ToolwrightError(f"{config_path}: verify.checks.{name} must be a table")
        command = entry.get("command")
        if not isinstance(command, str) or not command.strip():
            raise ToolwrightError(f"{config_path}: verify.checks.{name}.command is required")
        timeout = entry.get("timeout", default_timeout)
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ToolwrightError(f"{config_path}: verify.checks.{name}.timeout must be positive")
        inputs = entry.get("inputs", [])
        if not isinstance(inputs, list) or not all(isinstance(item, str) for item in inputs):
            raise ToolwrightError(f"{config_path}: verify.checks.{name}.inputs must be a list of paths")
        for item in inputs:
            candidate = Path(item)
            if candidate.is_absolute() or ".." in candidate.parts:
                raise ToolwrightError(f"{config_path}: verify.checks.{name}.inputs must stay inside the repository")
        checks[name] = Check(name=name, command=command, timeout=float(timeout), inputs=tuple(inputs))

    governance = data.get("governance", {})
    if not isinstance(governance, dict):
        raise ToolwrightError(f"{config_path}: governance must be a table")
    mode = governance.get("validator_mode", "advisory")
    if mode not in {"off", "advisory", "strict"}:
        raise ToolwrightError(f"{config_path}: governance.validator_mode must be off, advisory, or strict")
    return checks, governance


def classify_failure(name: str, exit_code: int, timed_out: bool) -> str:
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


def digest_input_paths(root: Path, inputs: tuple[str, ...]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(inputs):
        path = root / relative
        if not path.exists():
            raise ToolwrightError(f"cache input does not exist: {relative}")
        files = [path] if path.is_file() else sorted(item for item in path.rglob("*") if is_cache_input_file(item))
        for file in files:
            digest.update(file.relative_to(root).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(hashlib.sha256(file.read_bytes()).hexdigest().encode("ascii"))
            digest.update(b"\n")
    return digest.hexdigest()


def is_cache_input_file(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.name == ".DS_Store" or path.suffix in {".pyc", ".pyo"}:
        return False
    return not any(part in {"__pycache__", ".egg-info", "node_modules"} or part.endswith(".egg-info") for part in path.parts)


def cache_key(check: Check, root: Path) -> str:
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
        digest.update(digest_input_paths(root, check.inputs).encode("ascii"))
    return digest.hexdigest()


def truncate_output(value: str) -> str:
    return value if len(value) <= MAX_OUTPUT else value[-MAX_OUTPUT:]


def read_cached_result(path: Path, key: str, name: str) -> Result | None:
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


def write_cached_result(path: Path, key: str, result: Result) -> None:
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


def execute_check(root: Path, check: Check) -> Result:
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
            stdout=truncate_output(stdout),
            stderr=truncate_output(stderr or f"timed out after {check.timeout}s"),
            cached=False,
        )
    seconds = round(time.monotonic() - started, 2)
    exit_code = process.returncode
    return Result(
        name=check.name,
        status="pass" if exit_code == 0 else "fail",
        exit_code=exit_code,
        seconds=seconds,
        failure_class="" if exit_code == 0 else classify_failure(check.name, exit_code, False),
        stdout=truncate_output(process.stdout),
        stderr=truncate_output(process.stderr),
        cached=False,
    )


def run_verification_checks(
    root: Path,
    checks: dict[str, Check],
    only: list[str] | None = None,
    use_cache: bool = True,
    cache_dir: Path | None = None,
) -> list[Result]:
    selected = list(only) if only else list(checks)
    unknown = [name for name in selected if name not in checks]
    if unknown:
        raise ToolwrightError(f"unknown checks: {', '.join(unknown)}")
    directory = cache_dir or root / ".toolwright/cache/verify"
    results: list[Result] = []
    for name in selected:
        check = checks[name]
        key = cache_key(check, root)
        cached: Result | None = None
        if use_cache and check.inputs:
            cached = read_cached_result(directory / f"{name}.json", key, name)
        if cached is not None:
            results.append(cached)
            continue
        result = execute_check(root, check)
        if use_cache and check.inputs and result.status == "pass":
            write_cached_result(directory / f"{name}.json", key, result)
        results.append(result)
    return results


def summarize_results(results: list[Result]) -> dict[str, Any]:
    failures = [result for result in results if result.status == "fail"]
    return {
        "total": len(results),
        "passed": len(results) - len(failures),
        "failed": len(failures),
        "status": "fail" if failures else "pass",
        "failure_classes": sorted({result.failure_class for result in failures if result.failure_class}),
    }
