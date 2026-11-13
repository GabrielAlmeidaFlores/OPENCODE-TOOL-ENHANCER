"""
Adapter registry.

Public API: :func:`available_adapters`, :func:`get_adapter`, and :func:`plan`.

Side effects: none. Unknown adapters fail before any target file is touched.
"""
from __future__ import annotations
from ..constants import KEY_PLAN as EXPORT_PLAN
from ..constants import PAREN_CLOSE as MESSAGE_AVAILABLE_SUFFIX
from ..constants import SEPARATOR_COMMA_SPACE as SEPARATOR

from pathlib import Path

from ..locking import PlannedFile
from ..paths import ToolWrightError
from . import opencode
from .base import Adapter, is_generated_file

MESSAGE_UNKNOWN_ADAPTER = "unknown adapter: "
MESSAGE_AVAILABLE_PREFIX = " (available: "

_ADAPTERS: dict[str, Adapter] = {
    opencode.ADAPTER_NAME: Adapter(
        name=opencode.ADAPTER_NAME,
        supported_components=opencode.COMPONENTS,
        plan=opencode.plan,
    )
}


def available_adapters() -> tuple[str, ...]:
    return tuple(sorted(_ADAPTERS))


def get_adapter(name: str) -> Adapter:
    adapter = _ADAPTERS.get(name)
    if adapter is None:
        supported = SEPARATOR.join(available_adapters())
        raise ToolWrightError(f"{MESSAGE_UNKNOWN_ADAPTER}{name}{MESSAGE_AVAILABLE_PREFIX}{supported}{MESSAGE_AVAILABLE_SUFFIX}")
    return adapter


def plan(name: str, root: Path, target: Path, components: list[str]) -> list[PlannedFile]:
    return get_adapter(name).plan(root, target, components)


EXPORT_ADAPTER = "Adapter"
EXPORT_AVAILABLE = "available_adapters"
EXPORT_GET = "get_adapter"
EXPORT_GENERATED = "is_generated_file"

__all__ = [
    EXPORT_ADAPTER,
    EXPORT_AVAILABLE,
    EXPORT_GET,
    EXPORT_GENERATED,
    EXPORT_PLAN,
]
