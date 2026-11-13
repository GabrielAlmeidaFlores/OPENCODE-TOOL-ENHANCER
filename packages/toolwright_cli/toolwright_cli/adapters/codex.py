"""
OpenAI Codex adapter planning.

Public API: :func:`plan`.

Side effects: none.
"""
from __future__ import annotations
from ..constants import PLATFORM_CODEX as ADAPTER

from pathlib import Path

from ..locking import PlannedFile
from .content import codex_agent
from .strings import (
    AGENTS_FILE, AGENTS_GLOB, CODEX_AGENT_SUFFIX, CODEX_AGENTS_DIR, COMPONENT_AGENTS,
    COMPONENT_INSTRUCTIONS, UTF8,
)

COMPONENTS = frozenset({COMPONENT_AGENTS})
GENERATOR_AGENT = "codex.agent"
GENERATOR_INSTRUCTION = "codex.instructions"


def plan(root: Path, target: Path, components: list[str]) -> list[PlannedFile]:
    planned: list[PlannedFile] = []
    if COMPONENT_AGENTS in components:
        for source in sorted((root / COMPONENT_AGENTS).glob(AGENTS_GLOB)):
            role = source.parent.name
            planned.append(
                PlannedFile(
                    source,
                    target / CODEX_AGENTS_DIR / f"{role}{CODEX_AGENT_SUFFIX}",
                    COMPONENT_AGENTS,
                    ADAPTER,
                    GENERATOR_AGENT,
                    codex_agent(role, source.read_text(encoding=UTF8)),
                )
            )
    planned.append(
        PlannedFile(
            root / AGENTS_FILE,
            target / AGENTS_FILE,
            COMPONENT_INSTRUCTIONS,
            ADAPTER,
            GENERATOR_INSTRUCTION,
            (root / AGENTS_FILE).read_text(encoding=UTF8),
        )
    )
    return planned
