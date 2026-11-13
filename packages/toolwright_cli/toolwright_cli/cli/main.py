"""
CLI dispatch and top-level error handling.

Public API: :func:`main`.

Side effects: executes the selected command and prints errors to stderr.
"""
from __future__ import annotations
from .cli_strings import TEMPLATE_TOOLWRIGHT, TEMPLATE_TOOLWRIGHT_EXTERNAL_COMMAND_FAILED, TEMPLATE_TOOLWRIGHT_EXTERNAL_COMMAND_TIMED_OUT
from .cli_strings import (
    KEY_CATALOG,
    KEY_COMPAT,
    KEY_EVAL,
    KEY_GOVERN,
    KEY_MEMORY,
    KEY_SPEC,
    KEY_STATS,
    KEY_TASK,
)

import subprocess
import sys
from typing import Sequence

from ..constants import EMPTY_STRING
from ..cli_constants import (
    COMMAND_DOCTOR, COMMAND_INSTALL, COMMAND_PILOT, COMMAND_ROLLBACK,
    COMMAND_UNINSTALL, COMMAND_UPDATE, COMMAND_VERIFY, KEY_PROFILE,
)
from ..paths import ToolWrightError
from .common import resolve_repository_root
from .commands.analytics import _command_pilot, _command_stats
from .commands.lifecycle import (
    _command_doctor, _command_install, _command_rollback, _command_uninstall,
    _command_update,
)
from .commands.memory import _command_memory
from .commands.profiles import _command_catalog, _command_compat, _command_profile
from .commands.specs import _command_spec
from .commands.tasks import _command_task
from .commands.verification import _command_eval, _command_govern, _command_verify
from .parser import build_argument_parser

def main(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    handlers = {
        COMMAND_DOCTOR: _command_doctor,
        COMMAND_INSTALL: _command_install,
        COMMAND_UNINSTALL: _command_uninstall,
        COMMAND_UPDATE: _command_update,
        COMMAND_ROLLBACK: _command_rollback,
        KEY_PROFILE: _command_profile,
        KEY_CATALOG: _command_catalog,
        KEY_COMPAT: _command_compat,
        COMMAND_VERIFY: _command_verify,
        KEY_GOVERN: _command_govern,
        KEY_MEMORY: _command_memory,
        KEY_SPEC: _command_spec,
        KEY_STATS: _command_stats,
        KEY_EVAL: _command_eval,
        COMMAND_PILOT: _command_pilot,
        KEY_TASK: _command_task,
    }
    try:
        return handlers[args.command](args)
    except ToolWrightError as error:
        print(TEMPLATE_TOOLWRIGHT.format(error), file=sys.stderr)
        return error.exit_code
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or EMPTY_STRING).strip() or str(error)
        print(TEMPLATE_TOOLWRIGHT_EXTERNAL_COMMAND_FAILED.format(detail), file=sys.stderr)
        return 2
    except subprocess.TimeoutExpired as error:
        print(TEMPLATE_TOOLWRIGHT_EXTERNAL_COMMAND_TIMED_OUT.format(error), file=sys.stderr)
        return 2
    except (ValueError, OSError) as error:
        print(TEMPLATE_TOOLWRIGHT.format(error), file=sys.stderr)
        return 2
