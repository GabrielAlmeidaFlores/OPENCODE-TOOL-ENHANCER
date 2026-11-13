"""
OpenCode adapter planning.

Public API: :func:`plan`.

Side effects: none. The returned files are copied into ``.opencode/`` by the
installer, preserving the OpenCode behavior that existed before adapters were
introduced.
"""
from __future__ import annotations
from ..constants import MARKDOWN_SUFFIX
from ..constants import DEFAULT_ADAPTER as ADAPTER_NAME
from ..constants import DEFAULT_ADAPTER as COMPONENT_OPENCODE
from ..constants import GENERATOR_COPY
from ..constants import KEY_AGENTS as COMPONENT_AGENTS
from ..constants import KEY_COMMANDS as COMPONENT_COMMANDS
from ..constants import KEY_PLUGIN as COMPONENT_PLUGIN
from ..constants import KEY_RALPH as COMPONENT_RALPH
from ..constants import KEY_SKILLS as COMPONENT_SKILLS
from ..constants import TEXT_AGENT_MD as GLOB_AGENTS
from ..constants import TEXT_CONFIGS_OPENCODE_OPENCODE_JSONC as SOURCE_OPENCODE_CONFIG
from ..constants import TEXT_CONFIGS_RALPH_HATS as SOURCE_RALPH_HATS
from ..constants import TEXT_MD_2 as GLOB_COMMANDS
from ..constants import TEXT_OPENCODE_OPENCODE_JSONC as DEST_OPENCODE_CONFIG
from ..constants import TEXT_SKILL_MD as GLOB_SKILLS
from ..constants import TEXT_TEXT_2_3 as GLOB_ALL
from ..constants import TEXT_YML as GLOB_RALPH_HATS

from pathlib import Path

from ..locking import PlannedFile
from ..paths import ToolWrightError
from .base import is_generated_file



COMPONENTS = frozenset(
    {
        COMPONENT_OPENCODE,
        COMPONENT_AGENTS,
        COMPONENT_COMMANDS,
        COMPONENT_SKILLS,
        COMPONENT_RALPH,
        COMPONENT_PLUGIN,
    }
)

SOURCE_PLUGIN = "configs/opencode/plugins/toolwright-memory.js"
SOURCE_RALPH_CONFIG = "configs/ralph/ralph.yml"

DEST_AGENTS = ".opencode/agents"
DEST_COMMANDS = ".opencode/commands"
DEST_SKILLS = ".opencode/skills"
DEST_PLUGIN = ".opencode/plugins/toolwright-memory.js"
DEST_RALPH_CONFIG = ".ralph/ralph.yml"
DEST_RALPH_HATS = ".ralph/hats"

AGENT_FILENAME = "AGENT.md"
SKILL_DIRNAME = "SKILL.md"
MESSAGE_MISSING_SOURCE = "missing source file: "


def plan(root: Path, target: Path, components: list[str]) -> list[PlannedFile]:
    planned: list[PlannedFile] = []

    def add(source: Path, destination: Path, component: str) -> None:
        planned.append(
            PlannedFile(
                source=source,
                destination=destination,
                component=component,
                adapter=ADAPTER_NAME,
                generator=GENERATOR_COPY,
            )
        )

    if COMPONENT_OPENCODE in components:
        add(
            root / SOURCE_OPENCODE_CONFIG,
            target / DEST_OPENCODE_CONFIG,
            COMPONENT_OPENCODE,
        )
    if COMPONENT_AGENTS in components:
        for source in sorted((root / COMPONENT_AGENTS).glob(GLOB_AGENTS)):
            add(source, target / DEST_AGENTS / f"{source.parent.name}{MARKDOWN_SUFFIX}", COMPONENT_AGENTS)
    if COMPONENT_COMMANDS in components:
        for source in sorted((root / COMPONENT_COMMANDS).glob(GLOB_COMMANDS)):
            add(source, target / DEST_COMMANDS / source.name, COMPONENT_COMMANDS)
    if COMPONENT_SKILLS in components:
        for source in sorted((root / COMPONENT_SKILLS).glob(GLOB_SKILLS)):
            name = source.parent.name
            for file in sorted(source.parent.rglob(GLOB_ALL)):
                if file.is_file() and not is_generated_file(file):
                    relative = file.relative_to(source.parent)
                    add(file, target / DEST_SKILLS / name / relative, COMPONENT_SKILLS)
    if COMPONENT_PLUGIN in components:
        add(root / SOURCE_PLUGIN, target / DEST_PLUGIN, COMPONENT_PLUGIN)
    if COMPONENT_RALPH in components:
        add(root / SOURCE_RALPH_CONFIG, target / DEST_RALPH_CONFIG, COMPONENT_RALPH)
        for source in sorted((root / SOURCE_RALPH_HATS).glob(GLOB_RALPH_HATS)):
            add(source, target / DEST_RALPH_HATS / source.name, COMPONENT_RALPH)

    for item in planned:
        if not item.source.is_file():
            raise ToolWrightError(f"{MESSAGE_MISSING_SOURCE}{item.source}")
    return planned
