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
from .constants import COMMAND_FETCH
from .constants import GIT_FETCH_HEAD
from .constants import KEY_FINISHED_AT
from .constants import KEY_FOCUS
from .pilot_strings import (
    BASH,
    DEFAULT_ADAPTER,
    EMPTY_STRING,
    ENCODING_UTF8,
    FLAG_AGENT,
    FLAG_AUTO,
    FLAG_DEPTH,
    FLAG_DETACH,
    FLAG_FILTER_BLOB_NONE,
    FLAG_FORMAT,
    FLAG_MODEL,
    FLAG_NO_CHECKOUT,
    FLAG_STANDALONE,
    ISO_TIMESPEC,
    KEY_AGENT,
    KEY_ARTIFACTS,
    KEY_CHECKOUT,
    KEY_CLONE,
    KEY_COMMIT,
    KEY_COMPONENTS,
    KEY_COORDINATOR,
    KEY_COST,
    KEY_DRY_RUN,
    KEY_GIT,
    KEY_INPUT_TOKENS,
    KEY_JSON,
    KEY_MODEL,
    KEY_NAME,
    KEY_OPENCODE_EXIT,
    KEY_OPENCODE_STDERR,
    KEY_ORIGIN,
    KEY_OUTPUT_TOKENS,
    KEY_PILOT,
    KEY_PILOTS,
    KEY_PROFILE,
    KEY_PROMPT,
    KEY_REPOSITORY,
    KEY_RUN,
    KEY_SETUP_COMMAND,
    KEY_STACK,
    KEY_STARTED_AT,
    KEY_STEPS,
    KEY_SUCCESS,
    KEY_TOOL_CALLS,
    KEY_TOOL_ERRORS,
    KEY_VERIFICATION_COMMAND,
    KEY_VERIFICATION_EXIT,
    KEY_WALL_TIME_SECONDS,
    KEY_WORKSPACE,
    NEWLINE,
    SEPARATOR_COMMA_SPACE,
    SEPARATOR_SPACE,
    TEXT_1,
    TEXT_BASH_LC,
    TEXT_C,
    TEXT_COMMAND_EXIT,
    TEXT_CONFIGS_PILOTS_PILOTS_TOML,
    TEXT_GIT_CLONE_NO_CHECKOUT_FILTER_BLOB_NONE,
    TEXT_GIT_C_CHECKOUT_DETACH_FETCH_HEAD,
    TEXT_GIT_C_FETCH_DEPTH_1_ORIGIN,
    TEXT_GIT_FAILED,
    TEXT_INVALID_TOML,
    TEXT_IS_REQUIRED_FOR_A_REAL_PILOT_RUN,
    TEXT_LC,
    TEXT_META_JSON,
    TEXT_MISSING_PILOTS_NAME_TABLES,
    TEXT_OPENCODE_CONFIG,
    TEXT_OPENCODE_OPENCODE_JSONC,
    TEXT_OPENCODE_PILOT_MODEL,
    TEXT_OPENCODE_STANDALONE_RUN_AGENT_MODEL_AUTO_FORMAT_JSON_PROMPT,
    TEXT_PILOTS_MISSING,
    TEXT_PILOTS_MUST_BE_A_TABLE,
    TEXT_PILOT_CONFIGURATION_NOT_FOUND,
    TEXT_PILOT_RUN_PILOT_REPOSITORY_COMMIT_MODEL_OPENCODE_EXIT_SUCCES,
    TEXT_PILOT_SETUP_FAILED,
    TEXT_PROVIDER_MODEL,
    TEXT_PWD,
    TEXT_SESSION_JSONL,
    TEXT_SETUP_COMMAND,
    TEXT_SUMMARY_MD,
    TEXT_TOOLWRIGHT_INSTALL_PROFILE_TARGET_APPLY,
    TEXT_TOOLWRIGHT_PILOT,
    TEXT_UNKNOWN_PILOT_AVAILABLE,
    TEXT_VERIFICATION_COMMAND,
    TEXT_VERIFICATION_COMMAND_2,
    TEXT_VERIFICATION_LOG,
    TEXT_WORKSPACE_ALREADY_CONTAINS_A_CLONE,
)

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
from .paths import ToolWrightError
from .process import capture_command
from .profiles import load_profiles, resolve_components

CONFIG = Path(TEXT_CONFIGS_PILOTS_PILOTS_TOML)
REQUIRED = (KEY_REPOSITORY, KEY_COMMIT, KEY_STACK, KEY_FOCUS)


def load_pilots(root: Path) -> dict[str, dict[str, str]]:
    path = root / CONFIG
    if not path.is_file():
        raise ToolWrightError(TEXT_PILOT_CONFIGURATION_NOT_FOUND.format(path))
    try:
        data = tomllib.loads(path.read_text(encoding=ENCODING_UTF8))
    except tomllib.TOMLDecodeError as error:
        raise ToolWrightError(TEXT_INVALID_TOML.format(path, error)) from error
    pilots = data.get(KEY_PILOTS)
    if not isinstance(pilots, dict) or not pilots:
        raise ToolWrightError(TEXT_MISSING_PILOTS_NAME_TABLES.format(path))
    results: dict[str, dict[str, str]] = {}
    for name, entry in pilots.items():
        if not isinstance(entry, dict):
            raise ToolWrightError(TEXT_PILOTS_MUST_BE_A_TABLE.format(path, name))
        missing = [field for field in REQUIRED if not str(entry.get(field, EMPTY_STRING)).strip()]
        if missing:
            raise ToolWrightError(TEXT_PILOTS_MISSING.format(path, name, SEPARATOR_COMMA_SPACE.join(missing)))
        results[name] = {field: str(entry[field]) for field in REQUIRED}
    return results


def list_pilots(root: Path) -> list[dict[str, str]]:
    pilots = load_pilots(root)
    return [{KEY_NAME: name, **entry} for name, entry in sorted(pilots.items())]


def require_pilot_argument(value: str | None, label: str) -> str:
    if not value or not value.strip():
        raise ToolWrightError(TEXT_IS_REQUIRED_FOR_A_REAL_PILOT_RUN.format(label))
    return value.strip()


def run_git(args: list[str], cwd: Path | None = None, timeout: int = 1800) -> None:
    code, stdout, stderr = capture_command([KEY_GIT, *args], cwd=cwd, timeout=timeout)
    if code != 0:
        raise ToolWrightError(TEXT_GIT_FAILED.format(SEPARATOR_SPACE.join(args), stderr or stdout))


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
    agent: str = KEY_COORDINATOR,
    setup_command: str | None = None,
) -> dict[str, Any]:
    pilots = load_pilots(root)
    if name not in pilots:
        raise ToolWrightError(TEXT_UNKNOWN_PILOT_AVAILABLE.format(name, SEPARATOR_COMMA_SPACE.join(sorted(pilots))))
    pilot = pilots[name]
    profiles = load_profiles(root)
    components = resolve_components(profiles, profile, None)
    directory = workspace or Path(tempfile.mkdtemp(prefix=TEXT_TOOLWRIGHT_PILOT.format(name)))
    clone = directory / KEY_CLONE
    artifacts = directory / KEY_ARTIFACTS
    commands = [
        TEXT_GIT_CLONE_NO_CHECKOUT_FILTER_BLOB_NONE.format(pilot[KEY_REPOSITORY], clone),
        TEXT_GIT_C_FETCH_DEPTH_1_ORIGIN.format(clone, pilot[KEY_COMMIT]),
        TEXT_GIT_C_CHECKOUT_DETACH_FETCH_HEAD.format(clone),
        TEXT_TOOLWRIGHT_INSTALL_PROFILE_TARGET_APPLY.format(profile, clone),
        TEXT_BASH_LC.format(setup_command or TEXT_SETUP_COMMAND),
        TEXT_OPENCODE_STANDALONE_RUN_AGENT_MODEL_AUTO_FORMAT_JSON_PROMPT.format(agent, model or TEXT_PROVIDER_MODEL),
        TEXT_BASH_LC.format(verify_command or TEXT_VERIFICATION_COMMAND),
    ]
    if dry_run:
        return {
            KEY_PILOT: name,
            KEY_REPOSITORY: pilot[KEY_REPOSITORY],
            KEY_COMMIT: pilot[KEY_COMMIT],
            KEY_WORKSPACE: str(directory),
            KEY_PROFILE: profile,
            KEY_COMPONENTS: components,
            KEY_STEPS: commands,
            KEY_DRY_RUN: True,
        }

    prompt_value = require_pilot_argument(prompt, KEY_PROMPT)
    verify_value = require_pilot_argument(verify_command, TEXT_VERIFICATION_COMMAND_2)
    model_value = require_pilot_argument(model, TEXT_OPENCODE_PILOT_MODEL)
    directory.mkdir(parents=True, exist_ok=True)
    artifacts.mkdir(parents=True, exist_ok=True)
    if clone.exists():
        raise ToolWrightError(TEXT_WORKSPACE_ALREADY_CONTAINS_A_CLONE.format(clone))

    started = time.monotonic()
    started_at = datetime.now(timezone.utc).isoformat(timespec=ISO_TIMESPEC)
    try:
        run_git([KEY_CLONE, FLAG_NO_CHECKOUT, FLAG_FILTER_BLOB_NONE, pilot[KEY_REPOSITORY], str(clone)])
        run_git([TEXT_C, str(clone), COMMAND_FETCH, FLAG_DEPTH, TEXT_1, KEY_ORIGIN, pilot[KEY_COMMIT]])
        run_git([TEXT_C, str(clone), KEY_CHECKOUT, FLAG_DETACH, GIT_FETCH_HEAD])
        install(root=root, target=clone, profile=profile, components=components, apply=True)
        if setup_command:
            setup_code, setup_out, setup_err = capture_command(
                [BASH, TEXT_LC, setup_command],
                cwd=clone,
                timeout=1800,
            )
            if setup_code != 0:
                raise ToolWrightError(TEXT_PILOT_SETUP_FAILED.format(setup_err or setup_out))
        environment = dict(os.environ)
        environment[TEXT_PWD] = str(clone)
        environment[TEXT_OPENCODE_CONFIG] = str(clone / TEXT_OPENCODE_OPENCODE_JSONC)
        code, session, session_error = capture_command(
            [
                DEFAULT_ADAPTER,
                FLAG_STANDALONE,
                KEY_RUN,
                FLAG_AGENT,
                agent,
                FLAG_MODEL,
                model_value,
                FLAG_AUTO,
                FLAG_FORMAT,
                KEY_JSON,
                prompt_value,
            ],
            cwd=clone,
            env=environment,
            timeout=3600,
        )
        (artifacts / TEXT_SESSION_JSONL).write_text(session, encoding=ENCODING_UTF8)
        verify_code, verify_out, verify_err = capture_command([BASH, TEXT_LC, verify_value], cwd=clone, timeout=3600)
        (artifacts / TEXT_VERIFICATION_LOG).write_text(
            TEXT_COMMAND_EXIT.format(verify_value, verify_code, verify_out, verify_err),
            encoding=ENCODING_UTF8,
        )
        session_totals = stats.parse_session(artifacts / TEXT_SESSION_JSONL)
        result = {
            KEY_PILOT: name,
            KEY_REPOSITORY: pilot[KEY_REPOSITORY],
            KEY_COMMIT: pilot[KEY_COMMIT],
            KEY_PROFILE: profile,
            KEY_COMPONENTS: components,
            KEY_MODEL: model_value,
            KEY_AGENT: agent,
            KEY_PROMPT: prompt_value,
            KEY_VERIFICATION_COMMAND: verify_value,
            KEY_VERIFICATION_EXIT: verify_code,
            KEY_OPENCODE_EXIT: code,
            KEY_SETUP_COMMAND: setup_command,
            KEY_SUCCESS: verify_code == 0 and code == 0,
            KEY_OPENCODE_STDERR: session_error,
            KEY_STARTED_AT: started_at,
            KEY_FINISHED_AT: datetime.now(timezone.utc).isoformat(timespec=ISO_TIMESPEC),
            KEY_WALL_TIME_SECONDS: round(time.monotonic() - started, 2),
            KEY_COST: session_totals[KEY_COST],
            KEY_INPUT_TOKENS: session_totals[KEY_INPUT_TOKENS],
            KEY_OUTPUT_TOKENS: session_totals[KEY_OUTPUT_TOKENS],
            KEY_TOOL_CALLS: session_totals[KEY_TOOL_CALLS],
            KEY_TOOL_ERRORS: session_totals[KEY_TOOL_ERRORS],
            KEY_WORKSPACE: str(directory),
            KEY_DRY_RUN: False,
        }
        (artifacts / TEXT_META_JSON).write_text(json.dumps(result, indent=2, sort_keys=True) + NEWLINE, encoding=ENCODING_UTF8)
        (artifacts / TEXT_SUMMARY_MD).write_text(
            TEXT_PILOT_RUN_PILOT_REPOSITORY_COMMIT_MODEL_OPENCODE_EXIT_SUCCES.format(name, pilot[KEY_REPOSITORY], pilot[KEY_COMMIT], model_value, code, verify_code == 0 and code == 0, verify_code, session_totals[KEY_COST], session_totals[KEY_INPUT_TOKENS], session_totals[KEY_OUTPUT_TOKENS], session_totals[KEY_TOOL_CALLS], session_totals[KEY_TOOL_ERRORS], result[KEY_WALL_TIME_SECONDS]),
            encoding=ENCODING_UTF8,
        )
        return result
    finally:
        if clone.exists() and not keep:
            shutil.rmtree(clone, ignore_errors=True)
