"""
GitHub Copilot adapter planning.

Public API: :func:`plan`.

Side effects: none.
"""
from __future__ import annotations
from ..constants import PLATFORM_COPILOT as ADAPTER

from pathlib import Path

from ..locking import PlannedFile
from .content import copilot_instruction, markdown_command, skill_files
from .strings import (
    AGENTS_FILE, AGENTS_GLOB, COMMANDS_GLOB, COMPONENT_AGENTS, COMPONENT_COMMANDS,
    COMPONENT_COPY, COMPONENT_INSTRUCTIONS, COMPONENT_SKILLS, COPILOT_AGENT_SUFFIX,
    COPILOT_AGENTS_DIR, COPILOT_COMMANDS_DIR, COPILOT_FILE, COPILOT_PROMPT_SUFFIX,
    COPILOT_SKILLS_DIR, SKILLS_GLOB, UTF8,
)

COMPONENTS = frozenset({COMPONENT_AGENTS, COMPONENT_COMMANDS, COMPONENT_SKILLS})
GENERATOR_AGENT = "copilot.instruction"
GENERATOR_COMMAND = "copilot.prompt"
GENERATOR_INSTRUCTION = "copilot.instructions"


def plan(root: Path, target: Path, components: list[str]) -> list[PlannedFile]:
    planned: list[PlannedFile] = []
    if COMPONENT_AGENTS in components:
        for source in sorted((root / COMPONENT_AGENTS).glob(AGENTS_GLOB)):
            role = source.parent.name
            planned.append(
                PlannedFile(
                    source,
                    target / COPILOT_AGENTS_DIR / f"{role}{COPILOT_AGENT_SUFFIX}",
                    COMPONENT_AGENTS,
                    ADAPTER,
                    GENERATOR_AGENT,
                    copilot_instruction(role, source.read_text(encoding=UTF8)),
                )
            )
    if COMPONENT_COMMANDS in components:
        for source in sorted((root / COMPONENT_COMMANDS).glob(COMMANDS_GLOB)):
            planned.append(
                PlannedFile(
                    source,
                    target / COPILOT_COMMANDS_DIR / f"{source.stem}{COPILOT_PROMPT_SUFFIX}",
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
                        target / COPILOT_SKILLS_DIR / skill.parent.name / relative,
                        COMPONENT_SKILLS,
                        ADAPTER,
                        COMPONENT_COPY,
                    )
                )
    instructions = (root / AGENTS_FILE).read_text(encoding=UTF8)
    planned.append(
        PlannedFile(
            root / AGENTS_FILE,
            target / AGENTS_FILE,
            COMPONENT_INSTRUCTIONS,
            ADAPTER,
            GENERATOR_INSTRUCTION,
            instructions,
        )
    )
    planned.append(
        PlannedFile(
            root / AGENTS_FILE,
            target / COPILOT_FILE,
            COMPONENT_INSTRUCTIONS,
            ADAPTER,
            GENERATOR_INSTRUCTION,
            instructions,
        )
    )
    return planned
