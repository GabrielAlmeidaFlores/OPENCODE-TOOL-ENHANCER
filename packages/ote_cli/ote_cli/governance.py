"""
Governance contracts, budgets, loop detection, and risk gates.

Public API: :func:`load_agent_contracts`, :func:`evaluate_record`, and
:func:`required_gates_for_risk`.

Contracts are derived from the effective permissions in each
``agents/<role>/AGENT.md`` file, so there is one source of truth. Budgets and
loop thresholds come from the ``[governance]`` table in ``.ote/config.toml``.

Side effects: reads agent files and the configuration passed by the caller.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .paths import OteError

READ_ONLY_ROLES = {
    "coordinator",
    "planner",
    "researcher",
    "architect",
    "code-reviewer",
    "security-reviewer",
    "performance-analyst",
}

BUDGETS: tuple[tuple[str, str, str], ...] = (
    ("iterations", "max_iterations", "max_iterations"),
    ("tool_calls", "max_tool_calls", "max_tool_calls"),
    ("writes", "max_writes", "max_writes"),
    ("cost_usd", "max_cost_usd", "max_cost_usd"),
    ("delegation_depth", "max_delegation_depth", "max_delegation_depth"),
)

DEFAULTS: dict[str, float] = {
    "max_iterations": 40,
    "max_tool_calls": 200,
    "max_writes": 15,
    "max_cost_usd": 5.0,
    "max_delegation_depth": 2,
    "max_repeats": 2,
    "max_bounces": 3,
}

RISK_GATES: dict[str, tuple[str, ...]] = {
    "low": ("verify",),
    "medium": ("verify", "review"),
    "high": ("verify", "review", "security"),
}


def render_memory_frontmatter(path: Path) -> tuple[str, list[dict[str, str]]]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise OteError(f"{path}: missing frontmatter")
    end = text.find("\n---", 3)
    if end == -1:
        raise OteError(f"{path}: unterminated frontmatter")
    block = text[3:end].splitlines()
    mode = ""
    permissions: list[dict[str, str]] = []
    current: dict[str, str] = {}
    in_permissions = False
    for line in block:
        if line.startswith("mode:"):
            mode = line.split(":", 1)[1].strip()
        if line.startswith("permissions:"):
            in_permissions = True
            continue
        if not in_permissions:
            continue
        if line and not line.startswith((" ", "\t")):
            break
        match = re.match(r"\s*-\s*action:\s*\"?([^\"]+)\"?", line)
        if match:
            if current:
                permissions.append(current)
            current = {"action": match.group(1).strip()}
            continue
        match = re.match(r"\s*resource:\s*\"?(.*?)\"?\s*$", line)
        if match and current:
            current["resource"] = match.group(1).strip()
            continue
        match = re.match(r"\s*effect:\s*\"?(.*?)\"?\s*$", line)
        if match and current:
            current["effect"] = match.group(1).strip()
    if current:
        permissions.append(current)
    return mode, permissions


def load_agent_contracts(root: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    agents = sorted((root / "agents").glob("*/AGENT.md"))
    if not agents:
        raise OteError(f"no agents found under {root / 'agents'}")
    for path in agents:
        role = path.parent.name
        mode, permissions = render_memory_frontmatter(path)
        denied = {item["action"] for item in permissions if item.get("effect") == "deny"}
        allowed = {item["action"] for item in permissions if item.get("effect") == "allow"}
        read_only = role in READ_ONLY_ROLES
        violations: list[str] = []
        if role == "coordinator" and mode != "primary":
            violations.append("coordinator must be primary")
        if role != "coordinator" and mode != "subagent":
            violations.append("specialist must be subagent")
        if read_only and "edit" not in denied:
            violations.append("read-only role must deny edit")
        if not read_only and "edit" not in allowed:
            violations.append("write role must allow edit")
        results.append(
            {
                "agent": role,
                "mode": mode,
                "read_only": read_only,
                "denies_edit": "edit" in denied,
                "allowed_actions": sorted(allowed),
                "denied_actions": sorted(denied),
                "violations": violations,
                "status": "ok" if not violations else "fail",
            }
        )
    return results


def _number(settings: dict[str, Any], key: str) -> float:
    value = settings.get(key, DEFAULTS[key])
    if not isinstance(value, (int, float)) or value < 0:
        raise OteError(f"governance.{key} must be a non-negative number")
    return float(value)


def evaluate_record(record: dict[str, Any], settings: dict[str, Any]) -> dict[str, Any]:
    violations: list[dict[str, str]] = []
    for record_key, setting_key, label in BUDGETS:
        value = record.get(record_key, 0)
        if not isinstance(value, (int, float)) or value < 0:
            raise OteError(f"record.{record_key} must be a non-negative number")
        limit = _number(settings, setting_key)
        if value > limit:
            violations.append(
                {
                    "kind": "budget",
                    "detail": f"{record_key} {value} exceeds {label} {limit}",
                }
            )
    repeats = record.get("repeats", 0)
    if not isinstance(repeats, (int, float)) or repeats < 0:
        raise OteError("record.repeats must be a non-negative number")
    if repeats > _number(settings, "max_repeats"):
        violations.append(
            {
                "kind": "loop",
                "detail": f"repeated actions {repeats} exceed max_repeats {_number(settings, 'max_repeats')}",
            }
        )
    bounces = record.get("bounces", 0)
    if not isinstance(bounces, (int, float)) or bounces < 0:
        raise OteError("record.bounces must be a non-negative number")
    if bounces > _number(settings, "max_bounces"):
        violations.append(
            {
                "kind": "deadlock",
                "detail": f"handoff bounces {bounces} exceed max_bounces {_number(settings, 'max_bounces')}",
            }
        )
    return {
        "allowed": not violations,
        "violations": violations,
        "validator_mode": str(settings.get("validator_mode", "advisory")),
        "record": record,
    }


def required_gates_for_risk(risk: str) -> dict[str, Any]:
    key = risk.lower()
    if key not in RISK_GATES:
        raise OteError(f"unknown risk level: {risk}")
    return {"risk": key, "required": list(RISK_GATES[key])}
