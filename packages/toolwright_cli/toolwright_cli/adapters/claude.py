"""
Claude Code adapter planning.

Public API: :func:`plan`.

Side effects: none.
"""
from __future__ import annotations
from ..constants import PLATFORM_CLAUDE as ADAPTER

from pathlib import Path

from ..locking import PlannedFile
from .content import claude_agent, markdown_command, skill_files
from .strings import (
    AGENTS_FILE, AGENTS_GLOB, CLAUDE_AGENT_SUFFIX, CLAUDE_AGENTS_DIR, CLAUDE_COMMANDS_DIR,
    CLAUDE_FILE, CLAUDE_SKILLS_DIR, COMMANDS_GLOB, COMPONENT_AGENTS, COMPONENT_COMMANDS,
    COMPONENT_COPY, COMPONENT_INSTRUCTIONS, COMPONENT_SKILLS, SKILLS_GLOB, UTF8,
)

COMPONENTS = frozenset({COMPONENT_AGENTS, COMPONENT_COMMANDS, COMPONENT_SKILLS})
GENERATOR_AGENT = "claude.agent"
GENERATOR_COMMAND = "claude.command"
GENERATOR_INSTRUCTION = "claude.instruction"


def plan(root: Path, target: Path, components: list[str]) -> list[PlannedFile]:
    planned: list[PlannedFile] = []
    if COMPONENT_AGENTS in components:
        for source in sorted((root / COMPONENT_AGENTS).glob(AGENTS_GLOB)):
            role = source.parent.name
            planned.append(
                PlannedFile(
                    source,
                    target / CLAUDE_AGENTS_DIR / f"{role}{CLAUDE_AGENT_SUFFIX}",
                    COMPONENT_AGENTS,
                    ADAPTER,
                    GENERATOR_AGENT,
                    claude_agent(role, source.read_text(encoding=UTF8)),
                )
            )
    if COMPONENT_COMMANDS in components:
        for source in sorted((root / COMPONENT_COMMANDS).glob(COMMANDS_GLOB)):
            planned.append(
                PlannedFile(
                    source,
                    target / CLAUDE_COMMANDS_DIR / source.name,
                    COMPONENT_COMMANDS,
                    ADAPTER,
                    GENERATOR_COMMAND,
                    markdown_command(source.read_text(encoding=UTF8)),
                )
            )
    if COMPONENT_SKILLS in components:
        for skill in sorted((root / COMPONENT_SKILLS).glob(SKILLS_GLOB)):
            for file in skill_files(root, skill.parent.name):
                relative = file.relative_to(skill.parent)
                planned.append(
                    PlannedFile(
                        file,
                        target / CLAUDE_SKILLS_DIR / skill.parent.name / relative,
                        COMPONENT_SKILLS,
                        ADAPTER,
                        COMPONENT_COPY,
                    )
                )
    planned.append(
        PlannedFile(
            root / AGENTS_FILE,
            target / CLAUDE_FILE,
            COMPONENT_INSTRUCTIONS,
            ADAPTER,
            GENERATOR_INSTRUCTION,
            (root / AGENTS_FILE).read_text(encoding=UTF8),
        )
    )
    return planned
