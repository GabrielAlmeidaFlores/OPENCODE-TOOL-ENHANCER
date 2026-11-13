"""
ToolWright command-line package.

Public API: :func:`main` and :func:`build_argument_parser`.
"""
from __future__ import annotations
from .cli_strings import (
    KEY_BUILD_ARGUMENT_PARSER,
    KEY_DOCTOR_DICT,
    KEY_MAIN,
    KEY_RUN_DIAGNOSTIC_CHECKS,
    KEY_SUMMARIZE_CHECKS,
)

from ..doctor import checks_as_dict as doctor_dict
from ..doctor import run_diagnostic_checks, summarize_checks
from .main import main
from .parser import build_argument_parser

__all__ = [KEY_BUILD_ARGUMENT_PARSER, KEY_DOCTOR_DICT, KEY_MAIN, KEY_RUN_DIAGNOSTIC_CHECKS, KEY_SUMMARIZE_CHECKS]
