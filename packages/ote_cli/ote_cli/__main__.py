"""
Module entry point so ``python -m ote_cli`` behaves like the ``ote`` script.
"""
from __future__ import annotations

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
