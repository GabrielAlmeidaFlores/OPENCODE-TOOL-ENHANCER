"""
Shared adapter content generation.

Public API: :func:`frontmatter`, :func:`body`, :func:`claude_agent`,
:func:`codex_agent`, :func:`copilot_instruction`, :func:`markdown_command`,
:func:`skill_files`.

Side effects: none. All functions return values without touching the filesystem.
"""
from __future__ import annotations

import json
from pathlib import Path

from .strings import (
    AGENT_KEY,
    AGENT_PREFIX,
    AGENTS_GLOB,
    CLAUDE_AGENT_TEMPLATE,
    CODEX_AGENT_TEMPLATE,
    CODEX_READ_ONLY_SANDBOX,
    COMMAND_TEMPLATE,
    COMPONENT_SKILLS,
    COPILOT_INSTRUCTION_TEMPLATE,
    DESCRIPTION_KEY,
    DESCRIPTION_PREFIX,
    EDITOR_TOOLS,
    EMPTY,
    FRONTMATTER_END,
    FRONTMATTER_START,
    GLOB_ALL,
    NEWLINE,
    NODE_MODULES,
    PYCACHE,
    READ_ONLY_TOOLS,
    ROLE_AGENT_SUFFIX,
    ROLE_ARCHITECT,
    ROLE_CODE_REVIEWER,
    ROLE_COORDINATOR,
    ROLE_HYPHEN,
    ROLE_PERFORMANCE,
    ROLE_PLANNER,
    ROLE_RESEARCHER,
    ROLE_SECURITY,
    ROLE_UNDERSCORE,
    SKILLS_GLOB,
)

READ_ONLY_ROLES = frozenset(
    {
        ROLE_COORDINATOR,
        ROLE_PLANNER,
        ROLE_RESEARCHER,
        ROLE_ARCHITECT,
        ROLE_CODE_REVIEWER,
        ROLE_SECURITY,
        ROLE_PERFORMANCE,
    }
)


def _split(text: str) -> tuple[str, str]:
    if not text.startswith(FRONTMATTER_START):
        return EMPTY, text
    end = text.find(FRONTMATTER_END, len(FRONTMATTER_START))
    if end == -1:
        return EMPTY, text
    return text[len(FRONTMATTER_START) : end], text[end + len(FRONTMATTER_END) :]


def frontmatter(text: str) -> dict[str, str]:
    header, _ = _split(text)
    values: dict[str, str] = {}
    for line in header.splitlines():
        if line.startswith(DESCRIPTION_PREFIX):
            values[DESCRIPTION_KEY] = line.removeprefix(DESCRIPTION_PREFIX).strip()
        elif line.startswith(AGENT_PREFIX):
            values[AGENT_KEY] = line.removeprefix(AGENT_PREFIX).strip()
    return values


def body(text: str) -> str:
    _, content = _split(text)
    return content.strip() + NEWLINE


def claude_agent(role: str, text: str) -> str:
    metadata = frontmatter(text)
    description = metadata.get(DESCRIPTION_KEY, f"{role}{ROLE_AGENT_SUFFIX}")
    tools = READ_ONLY_TOOLS if role in READ_ONLY_ROLES else EDITOR_TOOLS
    return CLAUDE_AGENT_TEMPLATE.format(
        role=role, description=json.dumps(description), tools=tools, body=body(text)
    )


def codex_agent(role: str, text: str) -> str:
    metadata = frontmatter(text)
    name = role.replace(ROLE_HYPHEN, ROLE_UNDERSCORE)
    sandbox = CODEX_READ_ONLY_SANDBOX if role in READ_ONLY_ROLES else EMPTY
    return CODEX_AGENT_TEMPLATE.format(
        name=json.dumps(name),
        description=json.dumps(metadata.get(DESCRIPTION_KEY, f"{role}{ROLE_AGENT_SUFFIX}")),
        sandbox=sandbox,
        instructions=json.dumps(body(text)),
    )


def copilot_instruction(role: str, text: str) -> str:
    return COPILOT_INSTRUCTION_TEMPLATE.format(role=role, body=body(text))


def markdown_command(text: str) -> str:
    metadata = frontmatter(text)
    return COMMAND_TEMPLATE.format(
        description=json.dumps(metadata.get(DESCRIPTION_KEY, EMPTY)), body=body(text)
    )


def skill_files(root: Path, name: str) -> list[Path]:
    directory = root / COMPONENT_SKILLS / name
    return [
        path
        for path in sorted(directory.rglob(GLOB_ALL))
        if path.is_file() and PYCACHE not in path.parts and NODE_MODULES not in path.parts
    ]
