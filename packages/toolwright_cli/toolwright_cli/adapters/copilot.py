"""
GitHub Copilot adapter planning.

Public API: :func:`plan`.

Side effects: none.
"""
from __future__ import annotations

from pathlib import Path

from ..locking import PlannedFile
from .content import copilot_instruction, markdown_command, skill_files

ADAPTER = "copilot"
COMPONENTS = frozenset({"agents", "commands", "skills"})
GENERATOR_AGENT = "copilot.instruction"
GENERATOR_COMMAND = "copilot.prompt"
GENERATOR_INSTRUCTION = "copilot.instructions"


def plan(root: Path, target: Path, components: list[str]) -> list[PlannedFile]:
    planned: list[PlannedFile] = []
    if "agents" in components:
        for source in sorted((root / "agents").glob("*/AGENT.md")):
            role = source.parent.name
            planned.append(PlannedFile(source, target / ".github/instructions" / f"{role}.instructions.md", "agents", ADAPTER, GENERATOR_AGENT, copilot_instruction(role, source.read_text(encoding="utf-8"))))
    if "commands" in components:
        for source in sorted((root / "commands").glob("*.md")):
            planned.append(PlannedFile(source, target / ".github/prompts" / f"{source.stem}.prompt.md", "commands", ADAPTER, GENERATOR_COMMAND, markdown_command(source.read_text(encoding="utf-8"))))
    if "skills" in components:
        for skill in sorted((root / "skills").glob("*/SKILL.md")):
            for file in skill_files(root, skill.parent.name):
                relative = file.relative_to(skill.parent)
                planned.append(PlannedFile(file, target / ".github/skills" / skill.parent.name / relative, "skills", ADAPTER, "copy"))
    instructions = (root / "AGENTS.md").read_text(encoding="utf-8")
    planned.append(PlannedFile(root / "AGENTS.md", target / "AGENTS.md", "instructions", ADAPTER, GENERATOR_INSTRUCTION, instructions))
    planned.append(PlannedFile(root / "AGENTS.md", target / ".github/copilot-instructions.md", "instructions", ADAPTER, GENERATOR_INSTRUCTION, instructions))
    return planned
