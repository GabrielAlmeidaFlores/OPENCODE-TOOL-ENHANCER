"""
Shared adapter content generation.

Public API: :func:`frontmatter`, :func:`body`, :func:`claude_agent`,
:func:`codex_agent`, :func:`copilot_instruction`, :func:`markdown_command`.

Side effects: none. All functions return strings.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

READ_ONLY_ROLES = frozenset(
    {
        "coordinator",
        "planner",
        "researcher",
        "architect",
        "code-reviewer",
        "security-reviewer",
        "performance-analyst",
    }
)
EDITOR_ROLES = frozenset(
    {
        "backend-developer",
        "frontend-developer",
        "database-specialist",
        "test-engineer",
        "documentation-engineer",
    }
)


def _split(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[4:end], text[end + 5 :]


def frontmatter(text: str) -> dict[str, str]:
    header, _ = _split(text)
    values: dict[str, str] = {}
    for line in header.splitlines():
        if line.startswith("description: "):
            values["description"] = line.removeprefix("description: ").strip()
        elif line.startswith("agent: "):
            values["agent"] = line.removeprefix("agent: ").strip()
    return values


def body(text: str) -> str:
    _, content = _split(text)
    return content.strip() + "\n"


def _example_files(root: Path, component: str) -> list[Path]:
    if component == "agents":
        return sorted((root / "agents").glob("*/AGENT.md"))
    if component == "commands":
        return sorted((root / "commands").glob("*.md"))
    if component == "skills":
        return sorted((root / "skills").glob("*/SKILL.md"))
    return []


def claude_agent(role: str, text: str) -> str:
    metadata = frontmatter(text)
    description = metadata.get("description", f"{role} agent")
    tools = "Read, Grep, Glob" if role in READ_ONLY_ROLES else "Read, Grep, Glob, Edit, Write, Bash"
    return f"---\nname: {role}\ndescription: {json.dumps(description)}\ntools: {tools}\n---\n\n{body(text)}"


def codex_agent(role: str, text: str) -> str:
    metadata = frontmatter(text)
    name = role.replace("-", "_")
    return (
        f"name = {json.dumps(name)}\n"
        f"description = {json.dumps(metadata.get('description', f'{role} agent'))}\n"
        f"developer_instructions = {json.dumps(body(text))}\n"
    )


def copilot_instruction(role: str, text: str) -> str:
    return f"---\napplyTo: \"**/*\"\n---\n\n# {role}\n\n{body(text)}"


def markdown_command(text: str) -> str:
    metadata = frontmatter(text)
    description = metadata.get("description", "")
    return f"---\ndescription: {json.dumps(description)}\n---\n\n{body(text)}"


def skill_files(root: Path, name: str) -> list[Path]:
    directory = root / "skills" / name
    return [path for path in sorted(directory.rglob("*")) if path.is_file() and "__pycache__" not in path.parts and "node_modules" not in path.parts]
