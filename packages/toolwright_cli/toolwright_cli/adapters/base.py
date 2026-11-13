"""
Shared adapter contract.

Public API: :class:`Adapter` and :func:`is_generated_file`.

Side effects: none. Adapters only plan destinations; writing is centralized in
the installer so every platform gets the same backup, lock, and conflict rules.
"""
from __future__ import annotations
from ..constants import KEY_NODE_MODULES as GENERATED_DIR_NODE_MODULES
from ..constants import TEXT_DS_STORE as GENERATED_FILENAME_DS_STORE
from ..constants import TEXT_PYC as GENERATED_SUFFIX_PYC
from ..constants import TEXT_PYCACHE as GENERATED_DIR_PYCACHE
from ..constants import TEXT_PYO as GENERATED_SUFFIX_PYO

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from ..locking import PlannedFile


GENERATED_SUFFIXES = frozenset({GENERATED_SUFFIX_PYC, GENERATED_SUFFIX_PYO})


def is_generated_file(path: Path) -> bool:
    return (
        path.name == GENERATED_FILENAME_DS_STORE
        or path.suffix in GENERATED_SUFFIXES
        or GENERATED_DIR_PYCACHE in path.parts
        or GENERATED_DIR_NODE_MODULES in path.parts
    )


@dataclass(frozen=True)
class Adapter:

    name: str
    supported_components: frozenset[str]
    plan: Callable[[Path, Path, list[str]], list[PlannedFile]]
