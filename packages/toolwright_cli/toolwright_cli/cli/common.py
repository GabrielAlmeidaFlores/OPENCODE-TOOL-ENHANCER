"""
Shared CLI output and repository helpers.

Public API: :func:`emit_payload`, :func:`print_checks`,
:func:`print_install_result`, and :func:`resolve_repository_root`.

Side effects: writes to stdout only.
"""
from __future__ import annotations
from .cli_strings import TEMPLATE_CHECK_LINE, TEMPLATE_BACKUP, TEMPLATE_COMPONENTS_2, TEMPLATE_FILES_NEW_UPDATED_UNCHANGED, TEMPLATE_LOCK, TEMPLATE_PROFILE, TEMPLATE_SUMMARY_OK_WARN_FAIL, TEMPLATE_TARGET_2, TEMPLATE_TEMPLATE, TEMPLATE_TOOLS_MAY_INSTALL_GLOBALLY_USE_PROFILE_MINIMAL_TO_
from .cli_strings import (
    KEY_BACKUP,
    KEY_CODEGRAPH,
    KEY_LOCK,
    KEY_PLANNED,
    KEY_SERENA,
    KEY_SUMMARY,
    TEXT_AST_GREP,
    TEXT_PLAN_ONLY_RE_RUN_WITH_APPLY_TO_WRITE_THESE_FILES,
    TEXT_VERIFY_OPENCODE_STANDALONE_DEBUG_AGENTS,
)

import json
from pathlib import Path
from typing import Any

from ..constants import (
    KEY_APPLIED, KEY_COMPONENTS, KEY_MESSAGE, KEY_OUTPUT, KEY_PATH, KEY_PROFILE,
    KEY_TARGET, SEPARATOR_COMMA_SPACE, STATUS_FAIL, STATUS_NEW, STATUS_OK,
    STATUS_UNCHANGED, STATUS_UPDATED, STATUS_WARN,
)
from ..doctor import summarize_checks
from ..paths import find_repo_root

def emit_payload(payload: Any, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    if isinstance(payload, str):
        print(payload)


def print_checks(checks: list[Any]) -> None:
    width = max((len(check.id) for check in checks), default=0)
    for check in checks:
        print(TEMPLATE_CHECK_LINE.format(check.status.upper(), check.id, width, check.detail))
    summary = summarize_checks(checks)
    print(TEMPLATE_SUMMARY_OK_WARN_FAIL.format(summary[STATUS_OK], summary[STATUS_WARN], summary[STATUS_FAIL]))


def print_install_result(result: dict[str, Any]) -> None:
    print(TEMPLATE_TARGET_2.format(result[KEY_TARGET]))
    print(TEMPLATE_PROFILE.format(result[KEY_PROFILE]))
    print(TEMPLATE_COMPONENTS_2.format(SEPARATOR_COMMA_SPACE.join(result[KEY_COMPONENTS])))
    summary = result[KEY_SUMMARY]
    print(TEMPLATE_FILES_NEW_UPDATED_UNCHANGED.format(summary[STATUS_NEW], summary[STATUS_UPDATED], summary[STATUS_UNCHANGED]))
    tools = [component for component in result[KEY_COMPONENTS] if component in {TEXT_AST_GREP, KEY_SERENA, KEY_CODEGRAPH}]
    if tools:
        print(TEMPLATE_TOOLS_MAY_INSTALL_GLOBALLY_USE_PROFILE_MINIMAL_TO_.format(SEPARATOR_COMMA_SPACE.join(tools)))
    if result.get(KEY_OUTPUT):
        print(result[KEY_OUTPUT])
    if result[KEY_APPLIED]:
        if result.get(KEY_BACKUP):
            print(TEMPLATE_BACKUP.format(result[KEY_BACKUP]))
        if result.get(KEY_LOCK):
            print(TEMPLATE_LOCK.format(result[KEY_LOCK]))
        print(TEXT_VERIFY_OPENCODE_STANDALONE_DEBUG_AGENTS)
        return
    if result.get(KEY_MESSAGE):
        print(result[KEY_MESSAGE])
        return
    for path in result[KEY_PLANNED]:
        print(TEMPLATE_TEMPLATE.format(path))
    print(TEXT_PLAN_ONLY_RE_RUN_WITH_APPLY_TO_WRITE_THESE_FILES)


def resolve_repository_root(args: argparse.Namespace) -> Path:
    return find_repo_root(Path(args.repo) if args.repo else None)
