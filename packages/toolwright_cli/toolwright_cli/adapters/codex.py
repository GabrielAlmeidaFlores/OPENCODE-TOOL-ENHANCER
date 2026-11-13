"""
OpenAI Codex adapter planning.

Public API: :func:`plan`.

Side effects: none.
"""
from __future__ import annotations

from pathlib import Path

from ..locking import PlannedFile
from .content import codex_agent

ADAPTER = "codex"
COMPONENTS = frozenset({"agents"})
GENERATOR_AGENT = "codex.agent"
GENERATOR_INSTRUCTION = "codex.instructions"


def plan(root: Path, target: Path, components: list[str]) -> list[PlannedFile]:
    planned: list[PlannedFile] = []
    if "agents" in components:
        for source in sorted((root / "agents").glob("*/AGENT.md")):
            role = source.parent.name
            planned.append(PlannedFile(source, target / ".codex/agents" / f"{role}.toml", "agents", ADAPTER, GENERATOR_AGENT, codex_agent(role, source.read_text(encoding="utf-8"))))
    instructions = (root / "AGENTS.md").read_text(encoding="utf-8")
    planned.append(PlannedFile(root / "AGENTS.md", target / "AGENTS.md", "instructions", ADAPTER, GENERATOR_INSTRUCTION, instructions))
    return planned
