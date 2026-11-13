"""
Environment and repository diagnostics for ``toolwright doctor``.

Public API: :class:`Check`, :func:`run_diagnostic_checks`, and :func:`summarize_checks`.

Side effects: executes read-only commands such as ``opencode debug`` and the
repository validator. It never writes files.

Module constants: ``MIN_PYTHON`` is the oldest supported interpreter.
"""
from __future__ import annotations
from .constants import KEY_FILES, STATUS_FAIL
from .doctor_strings import (
    DEFAULT_ADAPTER,
    FLAG_STANDALONE,
    FLAG_VERSION,
    KEY_AGENTS,
    KEY_ARTIFACTS,
    KEY_CHECKS,
    KEY_COMMANDS,
    KEY_DETAIL,
    KEY_GIT,
    KEY_ID,
    KEY_LIST,
    KEY_LOCK,
    KEY_MCP,
    KEY_NODE,
    KEY_PATH,
    KEY_PYTHON,
    KEY_RALPH,
    KEY_REPOSITORY,
    KEY_RG,
    KEY_SKILLS,
    KEY_STATE,
    KEY_STATUS,
    KEY_SUMMARY,
    KEY_VALIDATOR,
    NEWLINE,
    SEPARATOR_COMMA_SPACE,
    STATUS_OK,
    STATUS_WARN,
    TEXT_AGENTS_COMMANDS_SKILLS_HATS,
    TEXT_AGENTS_COMMANDS_SKILLS_HATS_2,
    TEXT_AGENTS_COORDINATOR_AGENT_MD,
    TEXT_AGENT_MD,
    TEXT_CHECKED,
    TEXT_CHECKED_D,
    TEXT_CONFIGS_OPENCODE_OPENCODE_JSONC,
    TEXT_CONFIGS_RALPH_HATS,
    TEXT_DOCS_PROVENANCE_REGISTRY_YML,
    TEXT_D_D_D,
    TEXT_ERROR,
    TEXT_FILE_S_DIFFER_E_G,
    TEXT_IS_NOT_A_DIRECTORY,
    TEXT_IS_OLDER_THAN_3_11,
    TEXT_IS_V1_THIS_PROFILE_REQUIRES_V2,
    TEXT_LINE_S_REPORTED,
    TEXT_MANAGED_FILE_S_MATCH,
    TEXT_MCP_LIST_FAILED,
    TEXT_MD,
    TEXT_MISSING,
    TEXT_MISSING_2,
    TEXT_NOT_FOUND_ON_PATH,
    TEXT_NO_OPENCODE_OPENCODE_JSONC_IN_THE_TARGET_SKIPPING,
    TEXT_NO_TOOLWRIGHT_LOCK_JSON_IN_THE_TARGET_NOTHING_INSTALLED_BY_T,
    TEXT_NO_TOOLWRIGHT_STATE_JSON_YET,
    TEXT_OPENCODE_CONFIG,
    TEXT_OPENCODE_OPENCODE_JSONC,
    TEXT_OPENCODE_VERSION_FAILED,
    TEXT_SCRIPTS_INSTALLATION_INSTALL_SH,
    TEXT_SCRIPTS_VALIDATION_VALIDATE_CONFIG_PY,
    TEXT_SKILL_MD,
    TEXT_SKIPPED_BY_NO_MCP,
    TEXT_TEXT,
    TEXT_VALIDATOR_FAILED,
    TEXT_VERSION,
    TEXT_YML,
    TOOL_AST_GREP,
    TOOL_CODEGRAPH,
    TOOL_SERENA,
)

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
    version = TEXT_TEXT.format(current.major, current.minor, current.micro)
    if (current.major, current.minor) < MIN_PYTHON:
        return build_check_result(KEY_PYTHON, STATUS_FAIL, TEXT_IS_OLDER_THAN_3_11.format(version))
    return build_check_result(KEY_PYTHON, STATUS_OK, version)


def check_command_available(name: str, required: bool) -> Check:
    location = shutil.which(name)
    if location:
        return build_check_result(name, STATUS_OK, location)
    return build_check_result(name, STATUS_FAIL if required else STATUS_WARN, TEXT_NOT_FOUND_ON_PATH)


def check_repository_layout(root: Path) -> Check:
    required = [
        TEXT_VERSION,
        TEXT_CONFIGS_OPENCODE_OPENCODE_JSONC,
        TEXT_AGENTS_COORDINATOR_AGENT_MD,
        TEXT_SCRIPTS_INSTALLATION_INSTALL_SH,
        TEXT_DOCS_PROVENANCE_REGISTRY_YML,
    ]
    missing = [item for item in required if not (root / item).exists()]
    if missing:
        return build_check_result(KEY_REPOSITORY, STATUS_FAIL, TEXT_MISSING.format(SEPARATOR_COMMA_SPACE.join(missing)))
    return build_check_result(KEY_REPOSITORY, STATUS_OK, str(root))


def check_artifact_counts(root: Path) -> Check:
    agents = len(list((root / KEY_AGENTS).glob(TEXT_AGENT_MD)))
    commands = len(list((root / KEY_COMMANDS).glob(TEXT_MD)))
    skills = len(list((root / KEY_SKILLS).glob(TEXT_SKILL_MD)))
    hats = len(list((root / TEXT_CONFIGS_RALPH_HATS).glob(TEXT_YML)))
    if min(agents, commands, skills, hats) == 0:
        return build_check_result(KEY_ARTIFACTS, STATUS_FAIL, TEXT_AGENTS_COMMANDS_SKILLS_HATS_2.format(agents, commands, skills, hats))
    return build_check_result(
        KEY_ARTIFACTS,
        STATUS_OK,
        TEXT_AGENTS_COMMANDS_SKILLS_HATS.format(agents, commands, skills, hats),
    )


def check_opencode_version() -> Check:
    code, stdout, stderr = capture_command([DEFAULT_ADAPTER, FLAG_VERSION])
    if code != 0:
        return build_check_result(DEFAULT_ADAPTER, STATUS_FAIL, stderr or TEXT_OPENCODE_VERSION_FAILED)
    match = re.search(TEXT_D_D_D, stdout)
    if match is None:
        return build_check_result(DEFAULT_ADAPTER, STATUS_WARN, stdout)
    major = int(match.group(1))
    if major < 2:
        return build_check_result(DEFAULT_ADAPTER, STATUS_FAIL, TEXT_IS_V1_THIS_PROFILE_REQUIRES_V2.format(stdout))
    return build_check_result(DEFAULT_ADAPTER, STATUS_OK, stdout)


def run_repository_validator(root: Path) -> Check:
    script = root / TEXT_SCRIPTS_VALIDATION_VALIDATE_CONFIG_PY
    if not script.is_file():
        return build_check_result(KEY_VALIDATOR, STATUS_FAIL, TEXT_MISSING_2.format(script))
    code, stdout, stderr = capture_command([sys.executable, str(script)])
    if code != 0:
        lines = [line for line in (stdout + NEWLINE + stderr).splitlines() if line.startswith(TEXT_ERROR)]
        detail = lines[0] if lines else TEXT_VALIDATOR_FAILED
        return build_check_result(KEY_VALIDATOR, STATUS_FAIL, detail)
    count = re.search(TEXT_CHECKED_D, stdout)
    return build_check_result(KEY_VALIDATOR, STATUS_OK, TEXT_CHECKED.format(count.group(1)) if count else STATUS_OK)


def check_mcp_connections(target: Path) -> Check:
    config = target / TEXT_OPENCODE_OPENCODE_JSONC
    if not config.is_file():
        return build_check_result(KEY_MCP, STATUS_WARN, TEXT_NO_OPENCODE_OPENCODE_JSONC_IN_THE_TARGET_SKIPPING)
    environment = dict(os.environ)
    environment[TEXT_OPENCODE_CONFIG] = str(config)
    code, stdout, stderr = capture_command([DEFAULT_ADAPTER, FLAG_STANDALONE, KEY_MCP, KEY_LIST], cwd=target, env=environment)
    if code != 0:
        return build_check_result(KEY_MCP, STATUS_FAIL, (stderr or stdout or TEXT_MCP_LIST_FAILED).splitlines()[0])
    lines = [line for line in stdout.splitlines() if line.strip()]
    return build_check_result(KEY_MCP, STATUS_OK, TEXT_LINE_S_REPORTED.format(len(lines)))


def check_installation_lock(target: Path) -> Check:
    path = lock_path(target)
    if not path.is_file():
        return build_check_result(KEY_LOCK, STATUS_WARN, TEXT_NO_TOOLWRIGHT_LOCK_JSON_IN_THE_TARGET_NOTHING_INSTALLED_BY_T)
    try:
        lock = read_lock(path)
    except (ValueError, OSError) as error:
        return build_check_result(KEY_LOCK, STATUS_FAIL, str(error))
    drift = lock_drift(lock or {}, target)
    if drift:
        first = drift[0]
        return build_check_result(KEY_LOCK, STATUS_FAIL, TEXT_FILE_S_DIFFER_E_G.format(len(drift), first[KEY_PATH], first[KEY_STATUS]))
    return build_check_result(KEY_LOCK, STATUS_OK, TEXT_MANAGED_FILE_S_MATCH.format(len(lock.get(KEY_FILES, []))))


def check_cli_state(target: Path) -> Check:
    directory = state_path(target).parent
    if not directory.exists():
        return build_check_result(KEY_STATE, STATUS_WARN, TEXT_NO_TOOLWRIGHT_STATE_JSON_YET)
    if not directory.is_dir():
        return build_check_result(KEY_STATE, STATUS_FAIL, TEXT_IS_NOT_A_DIRECTORY.format(directory))
    return build_check_result(KEY_STATE, STATUS_OK, str(directory))


def run_diagnostic_checks(root: Path, target: Path, mcp: bool = True) -> list[Check]:
    checks = [
        check_python_version(),
        check_repository_layout(root),
        check_artifact_counts(root),
        check_command_available(KEY_GIT, required=True),
        check_opencode_version(),
        check_command_available(KEY_NODE, required=False),
        check_command_available(KEY_RG, required=False),
        check_command_available(TOOL_AST_GREP, required=False),
        check_command_available(TOOL_SERENA, required=False),
        check_command_available(TOOL_CODEGRAPH, required=False),
        check_command_available(KEY_RALPH, required=False),
        run_repository_validator(root),
        check_installation_lock(target),
        check_cli_state(target),
    ]
    if mcp:
        checks.append(check_mcp_connections(target))
    else:
        checks.append(build_check_result(KEY_MCP, STATUS_WARN, TEXT_SKIPPED_BY_NO_MCP))
    return checks


def summarize_checks(checks: list[Check]) -> dict[str, int]:
    summary = {STATUS_OK: 0, STATUS_WARN: 0, STATUS_FAIL: 0}
    for check in checks:
        summary[check.status] = summary.get(check.status, 0) + 1
    return summary


def checks_as_dict(checks: list[Check]) -> dict[str, Any]:
    return {
        KEY_CHECKS: [{KEY_ID: check.id, KEY_STATUS: check.status, KEY_DETAIL: check.detail} for check in checks],
        KEY_SUMMARY: summarize_checks(checks),
    }
