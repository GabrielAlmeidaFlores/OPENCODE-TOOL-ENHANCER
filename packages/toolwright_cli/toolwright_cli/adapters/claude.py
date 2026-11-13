"""
Claude Code adapter planning.

Public API: :func:`plan`.

Side effects: none.
"""
from __future__ import annotations

from pathlib import Path

from ..locking import PlannedFile
from .content import claude_agent, markdown_command, skill_files

ADAPTER = "claude"
COMPONENTS = frozenset({"agents", "commands", "skills"})
GENERATOR_AGENT = "claude.agent"
GENERATOR_COMMAND = "claude.command"
GENERATOR_INSTRUCTION = "claude.instruction"


def plan(root: Path, target: Path, components: list[str]) -> list[PlannedFile]:
    planned: list[PlannedFile] = []
    if "agents" in components:
        for source in sorted((root / "agents").glob("*/AGENT.md")):
            role = source.parent.name
            planned.append(PlannedFile(source, target / ".claude/agents" / f"{role}.md", "agents", ADAPTER, GENERATOR_AGENT, claude_agent(role, source.read_text(encoding="utf-8"))))
    if "commands" in components:
        for source in sorted((root / "commands").glob("*.md")):
            planned.append(PlannedFile(source, target / ".claude/commands" / source.name, "commands", ADAPTER, GENERATOR_COMMAND, markdown_command(source.read_text(encoding="utf-8"))))
    if "skills" in components:
        for skill in sorted((root / "skills").glob("*/SKILL.md")):
            for file in skill_files(root, skill.parent.name):
                relative = file.relative_to(skill.parent)
                planned.append(PlannedFile(file, target / ".claude/skills" / skill.parent.name / relative, "skills", ADAPTER, "copy"))
    planned.append(PlannedFile(root / "AGENTS.md", target / "CLAUDE.md", "instructions", ADAPTER, GENERATOR_INSTRUCTION, (root / "AGENTS.md").read_text(encoding="utf-8")))
    return planned
