"""
Governance contracts, budgets, loop detection, and risk gates.

Public API: :func:`load_agent_contracts`, :func:`evaluate_record`, and
:func:`required_gates_for_risk`.

Contracts are derived from the effective permissions in each
``agents/<role>/AGENT.md`` file, so there is one source of truth. Budgets and
loop thresholds come from the ``[governance]`` table in ``.toolwright/config.toml``.

Side effects: reads agent files and the configuration passed by the caller.
"""
from __future__ import annotations
from .constants import STATUS_FAIL
from .governance_strings import (
    EMPTY_STRING,
    ENCODING_UTF8,
    FLAG_TEXT,
    KEY_ACTION,
    KEY_ADVISORY,
    KEY_AGENT,
    KEY_AGENTS,
    KEY_ALLOW,
    KEY_ALLOWED,
    KEY_ALLOWED_ACTIONS,
    KEY_ARCHITECT,
    KEY_BOUNCES,
    KEY_BUDGET,
    KEY_COORDINATOR,
    KEY_COST_USD,
    KEY_DEADLOCK,
    KEY_DELEGATION_DEPTH,
    KEY_DENIED_ACTIONS,
    KEY_DENIES_EDIT,
    KEY_DENY,
    KEY_DETAIL,
    KEY_EDIT,
    KEY_EFFECT,
    KEY_HIGH,
    KEY_ITERATIONS,
    KEY_KIND,
    KEY_LOOP,
    KEY_LOW,
    KEY_MAX_BOUNCES,
    KEY_MAX_COST_USD,
    KEY_MAX_DELEGATION_DEPTH,
    KEY_MAX_ITERATIONS,
    KEY_MAX_REPEATS,
    KEY_MAX_TOOL_CALLS,
    KEY_MAX_WRITES,
    KEY_MEDIUM,
    KEY_MODE,
    KEY_PLANNER,
    KEY_PRIMARY,
    KEY_READ_ONLY,
    KEY_RECORD,
    KEY_REPEATS,
    KEY_REQUIRED,
    KEY_RESEARCHER,
    KEY_RESOURCE,
    KEY_REVIEW,
    KEY_RISK,
    KEY_SECURITY,
    KEY_STATUS,
    KEY_SUBAGENT,
    KEY_TOOL_CALLS,
    KEY_VALIDATOR_MODE,
    KEY_VERIFY,
    KEY_VIOLATIONS,
    KEY_WRITES,
    SEPARATOR_SPACE,
    STATUS_OK,
    TEXT_AGENT_MD,
    TEXT_CODE_REVIEWER,
    TEXT_COORDINATOR_MUST_BE_PRIMARY,
    TEXT_EXCEEDS,
    TEXT_GOVERNANCE_MUST_BE_A_NON_NEGATIVE_NUMBER,
    TEXT_HANDOFF_BOUNCES_EXCEED_MAX_BOUNCES,
    TEXT_MISSING_FRONTMATTER,
    TEXT_MODE,
    TEXT_NO_AGENTS_FOUND_UNDER,
    TEXT_PERFORMANCE_ANALYST,
    TEXT_PERMISSIONS,
    TEXT_READ_ONLY_ROLE_MUST_DENY_EDIT,
    TEXT_RECORD_BOUNCES_MUST_BE_A_NON_NEGATIVE_NUMBER,
    TEXT_RECORD_MUST_BE_A_NON_NEGATIVE_NUMBER,
    TEXT_RECORD_REPEATS_MUST_BE_A_NON_NEGATIVE_NUMBER,
    TEXT_REPEATED_ACTIONS_EXCEED_MAX_REPEATS,
    TEXT_SECURITY_REVIEWER,
    TEXT_SPECIALIST_MUST_BE_SUBAGENT,
    TEXT_S_EFFECT_S_S,
    TEXT_S_RESOURCE_S_S,
    TEXT_S_S_ACTION_S,
    TEXT_TEXT,
    TEXT_TEXT_2,
    TEXT_TEXT_3,
    TEXT_UNKNOWN_RISK_LEVEL,
    TEXT_UNTERMINATED_FRONTMATTER,
    TEXT_WRITE_ROLE_MUST_ALLOW_EDIT,
)

import re
from pathlib import Path
from typing import Any

from .paths import ToolWrightError

READ_ONLY_ROLES = {
    KEY_COORDINATOR,
    KEY_PLANNER,
    KEY_RESEARCHER,
    KEY_ARCHITECT,
    TEXT_CODE_REVIEWER,
    TEXT_SECURITY_REVIEWER,
    TEXT_PERFORMANCE_ANALYST,
}

BUDGETS: tuple[tuple[str, str, str], ...] = (
    (KEY_ITERATIONS, KEY_MAX_ITERATIONS, KEY_MAX_ITERATIONS),
    (KEY_TOOL_CALLS, KEY_MAX_TOOL_CALLS, KEY_MAX_TOOL_CALLS),
    (KEY_WRITES, KEY_MAX_WRITES, KEY_MAX_WRITES),
    (KEY_COST_USD, KEY_MAX_COST_USD, KEY_MAX_COST_USD),
    (KEY_DELEGATION_DEPTH, KEY_MAX_DELEGATION_DEPTH, KEY_MAX_DELEGATION_DEPTH),
)

DEFAULTS: dict[str, float] = {
    KEY_MAX_ITERATIONS: 40,
    KEY_MAX_TOOL_CALLS: 200,
    KEY_MAX_WRITES: 15,
    KEY_MAX_COST_USD: 5.0,
    KEY_MAX_DELEGATION_DEPTH: 2,
    KEY_MAX_REPEATS: 2,
    KEY_MAX_BOUNCES: 3,
}

RISK_GATES: dict[str, tuple[str, ...]] = {
    KEY_LOW: (KEY_VERIFY,),
    KEY_MEDIUM: (KEY_VERIFY, KEY_REVIEW),
    KEY_HIGH: (KEY_VERIFY, KEY_REVIEW, KEY_SECURITY),
}


def render_memory_frontmatter(path: Path) -> tuple[str, list[dict[str, str]]]:
    text = path.read_text(encoding=ENCODING_UTF8)
    if not text.startswith(FLAG_TEXT):
        raise ToolWrightError(TEXT_MISSING_FRONTMATTER.format(path))
    end = text.find(TEXT_TEXT, 3)
    if end == -1:
        raise ToolWrightError(TEXT_UNTERMINATED_FRONTMATTER.format(path))
    block = text[3:end].splitlines()
    mode = EMPTY_STRING
    permissions: list[dict[str, str]] = []
    current: dict[str, str] = {}
    in_permissions = False
    for line in block:
        if line.startswith(TEXT_MODE):
            mode = line.split(TEXT_TEXT_2, 1)[1].strip()
        if line.startswith(TEXT_PERMISSIONS):
            in_permissions = True
            continue
        if not in_permissions:
            continue
        if line and not line.startswith((SEPARATOR_SPACE, TEXT_TEXT_3)):
            break
        match = re.match(TEXT_S_S_ACTION_S, line)
        if match:
            if current:
                permissions.append(current)
            current = {KEY_ACTION: match.group(1).strip()}
            continue
        match = re.match(TEXT_S_RESOURCE_S_S, line)
        if match and current:
            current[KEY_RESOURCE] = match.group(1).strip()
            continue
        match = re.match(TEXT_S_EFFECT_S_S, line)
        if match and current:
            current[KEY_EFFECT] = match.group(1).strip()
    if current:
        permissions.append(current)
    return mode, permissions


def load_agent_contracts(root: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    agents = sorted((root / KEY_AGENTS).glob(TEXT_AGENT_MD))
    if not agents:
        raise ToolWrightError(TEXT_NO_AGENTS_FOUND_UNDER.format(root / KEY_AGENTS))
    for path in agents:
        role = path.parent.name
        mode, permissions = render_memory_frontmatter(path)
        denied = {item[KEY_ACTION] for item in permissions if item.get(KEY_EFFECT) == KEY_DENY}
        allowed = {item[KEY_ACTION] for item in permissions if item.get(KEY_EFFECT) == KEY_ALLOW}
        read_only = role in READ_ONLY_ROLES
        violations: list[str] = []
        if role == KEY_COORDINATOR and mode != KEY_PRIMARY:
            violations.append(TEXT_COORDINATOR_MUST_BE_PRIMARY)
        if role != KEY_COORDINATOR and mode != KEY_SUBAGENT:
            violations.append(TEXT_SPECIALIST_MUST_BE_SUBAGENT)
        if read_only and KEY_EDIT not in denied:
            violations.append(TEXT_READ_ONLY_ROLE_MUST_DENY_EDIT)
        if not read_only and KEY_EDIT not in allowed:
            violations.append(TEXT_WRITE_ROLE_MUST_ALLOW_EDIT)
        results.append(
            {
                KEY_AGENT: role,
                KEY_MODE: mode,
                KEY_READ_ONLY: read_only,
                KEY_DENIES_EDIT: KEY_EDIT in denied,
                KEY_ALLOWED_ACTIONS: sorted(allowed),
                KEY_DENIED_ACTIONS: sorted(denied),
                KEY_VIOLATIONS: violations,
                KEY_STATUS: STATUS_OK if not violations else STATUS_FAIL,
            }
        )
    return results


def _number(settings: dict[str, Any], key: str) -> float:
    value = settings.get(key, DEFAULTS[key])
    if not isinstance(value, (int, float)) or value < 0:
        raise ToolWrightError(TEXT_GOVERNANCE_MUST_BE_A_NON_NEGATIVE_NUMBER.format(key))
    return float(value)


def evaluate_record(record: dict[str, Any], settings: dict[str, Any]) -> dict[str, Any]:
    violations: list[dict[str, str]] = []
    for record_key, setting_key, label in BUDGETS:
        value = record.get(record_key, 0)
        if not isinstance(value, (int, float)) or value < 0:
            raise ToolWrightError(TEXT_RECORD_MUST_BE_A_NON_NEGATIVE_NUMBER.format(record_key))
        limit = _number(settings, setting_key)
        if value > limit:
            violations.append(
                {
                    KEY_KIND: KEY_BUDGET,
                    KEY_DETAIL: TEXT_EXCEEDS.format(record_key, value, label, limit),
                }
            )
    repeats = record.get(KEY_REPEATS, 0)
    if not isinstance(repeats, (int, float)) or repeats < 0:
        raise ToolWrightError(TEXT_RECORD_REPEATS_MUST_BE_A_NON_NEGATIVE_NUMBER)
    if repeats > _number(settings, KEY_MAX_REPEATS):
        violations.append(
            {
                KEY_KIND: KEY_LOOP,
                KEY_DETAIL: TEXT_REPEATED_ACTIONS_EXCEED_MAX_REPEATS.format(repeats, _number(settings, KEY_MAX_REPEATS)),
            }
        )
    bounces = record.get(KEY_BOUNCES, 0)
    if not isinstance(bounces, (int, float)) or bounces < 0:
        raise ToolWrightError(TEXT_RECORD_BOUNCES_MUST_BE_A_NON_NEGATIVE_NUMBER)
    if bounces > _number(settings, KEY_MAX_BOUNCES):
        violations.append(
            {
                KEY_KIND: KEY_DEADLOCK,
                KEY_DETAIL: TEXT_HANDOFF_BOUNCES_EXCEED_MAX_BOUNCES.format(bounces, _number(settings, KEY_MAX_BOUNCES)),
            }
        )
    return {
        KEY_ALLOWED: not violations,
        KEY_VIOLATIONS: violations,
        KEY_VALIDATOR_MODE: str(settings.get(KEY_VALIDATOR_MODE, KEY_ADVISORY)),
        KEY_RECORD: record,
    }


def required_gates_for_risk(risk: str) -> dict[str, Any]:
    key = risk.lower()
    if key not in RISK_GATES:
        raise ToolWrightError(TEXT_UNKNOWN_RISK_LEVEL.format(risk))
    return {KEY_RISK: key, KEY_REQUIRED: list(RISK_GATES[key])}
