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
from .constants import STATUS_FAIL, KEY_FAILURE_CLASS, KEY_FAILURE_CLASSES, KEY_FAILED
from .verify_strings import (
    EMPTY_STRING,
    ENCODING_UTF8,
    ISO_TIMESPEC,
    KEY_ADVISORY,
    KEY_ASCII,
    KEY_CHECKS,
    KEY_COMMAND,
    KEY_EXIT_CODE,
    KEY_GOVERNANCE,
    KEY_INPUTS,
    KEY_KEY,
    KEY_LINT,
    KEY_NODE_MODULES,
    KEY_OFF,
    KEY_PASS,
    KEY_PASSED,
    KEY_PERMISSION,
    KEY_SCHEMA_VERSION,
    KEY_SECURITY,
    KEY_STATUS,
    KEY_STDERR,
    KEY_STDOUT,
    KEY_STRICT,
    KEY_TEST,
    KEY_TIMEOUT,
    KEY_TOTAL,
    KEY_TYPE,
    KEY_VALIDATE,
    KEY_VALIDATOR_MODE,
    KEY_VERIFY,
    NEWLINE,
    SEPARATOR_COMMA_SPACE,
    TEXT_A_Z0_9_A_Z0_9,
    TEXT_CACHE_INPUT_DOES_NOT_EXIST,
    TEXT_COMMAND_FAILURE,
    TEXT_CONFIGURATION_MUST_BE_A_TABLE,
    TEXT_DS_STORE,
    TEXT_EGG_INFO,
    TEXT_GOVERNANCE_MUST_BE_A_TABLE,
    TEXT_GOVERNANCE_VALIDATOR_MODE_MUST_BE_OFF_ADVISORY_OR_STRICT,
    TEXT_INVALID_CHECK_NAME,
    TEXT_INVALID_TOML,
    TEXT_JSON,
    TEXT_LINT_FAILURE,
    TEXT_MISSING_COMMAND,
    TEXT_MISSING_VERIFICATION_CONFIG,
    TEXT_MISSING_VERIFY_CHECKS_NAME_TABLES,
    TEXT_MISSING_VERIFY_TABLE,
    TEXT_PYC,
    TEXT_PYCACHE,
    TEXT_PYO,
    TEXT_SECURITY_FAILURE,
    TEXT_TEST_FAILURE,
    TEXT_TEXT,
    TEXT_TEXT_2,
    TEXT_TIMED_OUT_AFTER_S,
    TEXT_TOOLWRIGHT_CACHE_VERIFY,
    TEXT_TOOLWRIGHT_CONFIG_TOML,
    TEXT_TYPE_FAILURE,
    TEXT_UNKNOWN_CHECKS,
    TEXT_VALIDATION_FAILURE,
    TEXT_VERIFY_CHECKS_COMMAND_IS_REQUIRED,
    TEXT_VERIFY_CHECKS_INPUTS_MUST_BE_A_LIST_OF_PATHS,
    TEXT_VERIFY_CHECKS_INPUTS_MUST_STAY_INSIDE_THE_REPOSITORY,
    TEXT_VERIFY_CHECKS_MUST_BE_A_TABLE,
    TEXT_VERIFY_CHECKS_TIMEOUT_MUST_BE_POSITIVE,
    TEXT_VERIFY_TIMEOUT_MUST_BE_A_POSITIVE_NUMBER,
)

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

from .paths import ToolWrightError

DEFAULT_TIMEOUT = 900
MAX_OUTPUT = 8000
CACHE_SCHEMA_VERSION = 1
NAME_PATTERN = TEXT_A_Z0_9_A_Z0_9


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
        raise ToolWrightError(TEXT_INVALID_CHECK_NAME.format(name))


def load_verification_config(root: Path, path: Path | None = None) -> tuple[dict[str, Check], dict[str, Any]]:
    config_path = path or root / TEXT_TOOLWRIGHT_CONFIG_TOML
    if not config_path.is_file():
        raise ToolWrightError(TEXT_MISSING_VERIFICATION_CONFIG.format(config_path))
    try:
        data = tomllib.loads(config_path.read_text(encoding=ENCODING_UTF8))
    except tomllib.TOMLDecodeError as error:
        raise ToolWrightError(TEXT_INVALID_TOML.format(config_path, error)) from error
    if not isinstance(data, dict):
        raise ToolWrightError(TEXT_CONFIGURATION_MUST_BE_A_TABLE.format(config_path))

    verify_section = data.get(KEY_VERIFY)
    if not isinstance(verify_section, dict):
        raise ToolWrightError(TEXT_MISSING_VERIFY_TABLE.format(config_path))
    default_timeout = verify_section.get(KEY_TIMEOUT, DEFAULT_TIMEOUT)
    if not isinstance(default_timeout, (int, float)) or default_timeout <= 0:
        raise ToolWrightError(TEXT_VERIFY_TIMEOUT_MUST_BE_A_POSITIVE_NUMBER.format(config_path))

    checks_section = verify_section.get(KEY_CHECKS)
    if not isinstance(checks_section, dict) or not checks_section:
        raise ToolWrightError(TEXT_MISSING_VERIFY_CHECKS_NAME_TABLES.format(config_path))

    checks: dict[str, Check] = {}
    for name, entry in checks_section.items():
        validate_check_name(name)
        if not isinstance(entry, dict):
            raise ToolWrightError(TEXT_VERIFY_CHECKS_MUST_BE_A_TABLE.format(config_path, name))
        command = entry.get(KEY_COMMAND)
        if not isinstance(command, str) or not command.strip():
            raise ToolWrightError(TEXT_VERIFY_CHECKS_COMMAND_IS_REQUIRED.format(config_path, name))
        timeout = entry.get(KEY_TIMEOUT, default_timeout)
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ToolWrightError(TEXT_VERIFY_CHECKS_TIMEOUT_MUST_BE_POSITIVE.format(config_path, name))
        inputs = entry.get(KEY_INPUTS, [])
        if not isinstance(inputs, list) or not all(isinstance(item, str) for item in inputs):
            raise ToolWrightError(TEXT_VERIFY_CHECKS_INPUTS_MUST_BE_A_LIST_OF_PATHS.format(config_path, name))
        for item in inputs:
            candidate = Path(item)
            if candidate.is_absolute() or TEXT_TEXT in candidate.parts:
                raise ToolWrightError(TEXT_VERIFY_CHECKS_INPUTS_MUST_STAY_INSIDE_THE_REPOSITORY.format(config_path, name))
        checks[name] = Check(name=name, command=command, timeout=float(timeout), inputs=tuple(inputs))

    governance = data.get(KEY_GOVERNANCE, {})
    if not isinstance(governance, dict):
        raise ToolWrightError(TEXT_GOVERNANCE_MUST_BE_A_TABLE.format(config_path))
    mode = governance.get(KEY_VALIDATOR_MODE, KEY_ADVISORY)
    if mode not in {KEY_OFF, KEY_ADVISORY, KEY_STRICT}:
        raise ToolWrightError(TEXT_GOVERNANCE_VALIDATOR_MODE_MUST_BE_OFF_ADVISORY_OR_STRICT.format(config_path))
    return checks, governance


def classify_failure(name: str, exit_code: int, timed_out: bool) -> str:
    if timed_out:
        return KEY_TIMEOUT
    if exit_code == 127:
        return TEXT_MISSING_COMMAND
    if exit_code == 126:
        return KEY_PERMISSION
    lowered = name.lower()
    for token, label in (
        (KEY_TEST, TEXT_TEST_FAILURE),
        (KEY_LINT, TEXT_LINT_FAILURE),
        (KEY_TYPE, TEXT_TYPE_FAILURE),
        (KEY_VALIDATE, TEXT_VALIDATION_FAILURE),
        (KEY_SECURITY, TEXT_SECURITY_FAILURE),
    ):
        if token in lowered:
            return label
    return TEXT_COMMAND_FAILURE


def digest_input_paths(root: Path, inputs: tuple[str, ...]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(inputs):
        path = root / relative
        if not path.exists():
            raise ToolWrightError(TEXT_CACHE_INPUT_DOES_NOT_EXIST.format(relative))
        files = [path] if path.is_file() else sorted(item for item in path.rglob(TEXT_TEXT_2) if is_cache_input_file(item))
        for file in files:
            digest.update(file.relative_to(root).as_posix().encode(ENCODING_UTF8))
            digest.update(b"\0")
            digest.update(hashlib.sha256(file.read_bytes()).hexdigest().encode(KEY_ASCII))
            digest.update(b"\n")
    return digest.hexdigest()


def is_cache_input_file(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.name == TEXT_DS_STORE or path.suffix in {TEXT_PYC, TEXT_PYO}:
        return False
    return not any(part in {TEXT_PYCACHE, TEXT_EGG_INFO, KEY_NODE_MODULES} or part.endswith(TEXT_EGG_INFO) for part in path.parts)


def cache_key(check: Check, root: Path) -> str:
    digest = hashlib.sha256()
    digest.update(check.name.encode(ENCODING_UTF8))
    digest.update(b"\0")
    digest.update(check.command.encode(ENCODING_UTF8))
    digest.update(b"\0")
    digest.update(check.timeout.__repr__().encode(KEY_ASCII))
    digest.update(b"\0")
    digest.update(sys.version.encode(ENCODING_UTF8))
    if check.inputs:
        digest.update(b"\0")
        digest.update(digest_input_paths(root, check.inputs).encode(KEY_ASCII))
    return digest.hexdigest()


def truncate_output(value: str) -> str:
    return value if len(value) <= MAX_OUTPUT else value[-MAX_OUTPUT:]


def read_cached_result(path: Path, key: str, name: str) -> Result | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding=ENCODING_UTF8))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(data, dict):
        return None
    if data.get(KEY_SCHEMA_VERSION) != CACHE_SCHEMA_VERSION or data.get(KEY_KEY) != key:
        return None
    if data.get(KEY_STATUS) != KEY_PASS:
        return None
    try:
        return Result(
            name=name,
            status=str(data.get(KEY_STATUS, STATUS_FAIL)),
            exit_code=int(data.get(KEY_EXIT_CODE, 1)),
            seconds=float(data.get(ISO_TIMESPEC, 0)),
            failure_class=str(data.get(KEY_FAILURE_CLASS, TEXT_COMMAND_FAILURE)),
            stdout=str(data.get(KEY_STDOUT, EMPTY_STRING)),
            stderr=str(data.get(KEY_STDERR, EMPTY_STRING)),
            cached=True,
        )
    except (TypeError, ValueError):
        return None


def write_cached_result(path: Path, key: str, result: Result) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        KEY_SCHEMA_VERSION: CACHE_SCHEMA_VERSION,
        KEY_KEY: key,
        KEY_STATUS: result.status,
        KEY_EXIT_CODE: result.exit_code,
        ISO_TIMESPEC: result.seconds,
        KEY_FAILURE_CLASS: result.failure_class,
        KEY_STDOUT: result.stdout,
        KEY_STDERR: result.stderr,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + NEWLINE, encoding=ENCODING_UTF8)


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
        stdout = error.stdout.decode() if isinstance(error.stdout, bytes) else (error.stdout or EMPTY_STRING)
        stderr = error.stderr.decode() if isinstance(error.stderr, bytes) else (error.stderr or EMPTY_STRING)
        return Result(
            name=check.name,
            status=STATUS_FAIL,
            exit_code=124,
            seconds=round(time.monotonic() - started, 2),
            failure_class=KEY_TIMEOUT,
            stdout=truncate_output(stdout),
            stderr=truncate_output(stderr or TEXT_TIMED_OUT_AFTER_S.format(check.timeout)),
            cached=False,
        )
    seconds = round(time.monotonic() - started, 2)
    exit_code = process.returncode
    return Result(
        name=check.name,
        status=KEY_PASS if exit_code == 0 else STATUS_FAIL,
        exit_code=exit_code,
        seconds=seconds,
        failure_class=EMPTY_STRING if exit_code == 0 else classify_failure(check.name, exit_code, False),
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
        raise ToolWrightError(TEXT_UNKNOWN_CHECKS.format(SEPARATOR_COMMA_SPACE.join(unknown)))
    directory = cache_dir or root / TEXT_TOOLWRIGHT_CACHE_VERIFY
    results: list[Result] = []
    for name in selected:
        check = checks[name]
        key = cache_key(check, root)
        cached: Result | None = None
        if use_cache and check.inputs:
            cached = read_cached_result(directory / TEXT_JSON.format(name), key, name)
        if cached is not None:
            results.append(cached)
            continue
        result = execute_check(root, check)
        if use_cache and check.inputs and result.status == KEY_PASS:
            write_cached_result(directory / TEXT_JSON.format(name), key, result)
        results.append(result)
    return results


def summarize_results(results: list[Result]) -> dict[str, Any]:
    failures = [result for result in results if result.status == STATUS_FAIL]
    return {
        KEY_TOTAL: len(results),
        KEY_PASSED: len(results) - len(failures),
        KEY_FAILED: len(failures),
        KEY_STATUS: STATUS_FAIL if failures else KEY_PASS,
        KEY_FAILURE_CLASSES: sorted({result.failure_class for result in failures if result.failure_class}),
    }
