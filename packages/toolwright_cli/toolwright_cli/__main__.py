"""
Module entry point so ``python -m toolwright_cli`` behaves like the ``toolwright`` script.
"""
from __future__ import annotations
from .__main___strings import (
    TEXT_MAIN,
)

import sys

from .cli import main

if __name__ == TEXT_MAIN:
    sys.exit(main())
