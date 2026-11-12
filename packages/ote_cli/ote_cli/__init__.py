"""
OpenCode Tool Enhancer command-line interface.

Public API: ``__version__`` and the ``main`` entry point exported from
:mod:`ote_cli.cli`.

The package has no runtime dependencies outside the Python standard library.
Side effects are limited to the commands that explicitly write files.
"""
from __future__ import annotations

import importlib.metadata
from pathlib import Path

_PACKAGE_DIR = Path(__file__).resolve().parent
_REPO_VERSION = _PACKAGE_DIR.parents[2] / "VERSION"


def _detect_version() -> str:
    if _REPO_VERSION.is_file():
        return _REPO_VERSION.read_text(encoding="utf-8").strip()
    try:
        return importlib.metadata.version("ote-cli")
    except importlib.metadata.PackageNotFoundError:
        return "0.0.0"


__version__ = _detect_version()

__all__ = ["__version__"]
