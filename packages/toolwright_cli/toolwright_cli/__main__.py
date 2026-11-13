"""
Module entry point so ``python -m toolwright_cli`` behaves like the ``toolwright`` script.
"""
from __future__ import annotations

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
