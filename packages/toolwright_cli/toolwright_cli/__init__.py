"""
ToolWright command-line interface.

Public API: ``__version__`` and the ``main`` entry point exported from
:mod:`toolwright_cli.cli`.

The package has no runtime dependencies outside the Python standard library.
Side effects are limited to the commands that explicitly write files.
"""
from __future__ import annotations
from .__init___strings import (
    ENCODING_UTF8,
    TEXT_0_0_0,
    TEXT_TOOLWRIGHT_CLI,
    TEXT_VERSION,
    TEXT_VERSION_2,
)

import importlib.metadata
from pathlib import Path

_PACKAGE_DIR = Path(__file__).resolve().parent
_REPO_VERSION = _PACKAGE_DIR.parents[2] / TEXT_VERSION


def _detect_version() -> str:
    if _REPO_VERSION.is_file():
        return _REPO_VERSION.read_text(encoding=ENCODING_UTF8).strip()
    try:
        return importlib.metadata.version(TEXT_TOOLWRIGHT_CLI)
    except importlib.metadata.PackageNotFoundError:
        return TEXT_0_0_0


__version__ = _detect_version()

__all__ = [TEXT_VERSION_2]
