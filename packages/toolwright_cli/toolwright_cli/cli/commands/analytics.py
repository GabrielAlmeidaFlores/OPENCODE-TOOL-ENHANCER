"""
Stats and pilot command handlers.

Public API: command handler functions used by :mod:`toolwright_cli.cli.main`.

Side effects: reads benchmark artifacts and delegates to the pilot runner.
"""
from __future__ import annotations
from ..cli_strings import TEMPLATE_20_22, TEMPLATE_ARTIFACTS_ARTIFACTS, TEMPLATE_BUDGET_EXCEEDED_6F_6F, TEMPLATE_COST_6F, TEMPLATE_OPENCODE_EXIT, TEMPLATE_PILOT, TEMPLATE_SUCCESS, TEMPLATE_TEMPLATE, TEMPLATE_VERIFICATION_EXIT, TEMPLATE_WORKSPACE
from ..cli_strings import (
    KEY_COMMIT,
    KEY_COST,
    KEY_CSV,
    KEY_DRY_RUN,
    KEY_FOCUS,
    KEY_OPENCODE_EXIT,
    KEY_PILOTS,
    KEY_STACK,
    KEY_STEPS,
    KEY_SUCCESS,
    KEY_VERIFICATION_EXIT,
    KEY_WORKSPACE,
    TEXT_BENCHMARKS_RESULTS,
    TEXT_OPENCODE_PILOT_MODEL,
)

import argparse
import os
import sys
from pathlib import Path

from ..common import emit_payload, resolve_repository_root
from ...constants import KEY_FAILURES, KEY_NAME, KEY_RESULTS, KEY_STATUS, NEWLINE, STATUS_FAIL
from ...cli_constants import (
    COMMAND_LIST, COMMAND_PILOT, EMPTY_STRING, FORMAT_JSON, FORMAT_MARKDOWN,
)
from ... import pilot as pilot_module
from ... import stats as stats_module
from ...paths import ToolWrightError

def _command_stats(args: argparse.Namespace) -> int:
    root = resolve_repository_root(args)
    paths = [Path(item).expanduser() for item in (args.results or [str(root / TEXT_BENCHMARKS_RESULTS)])]
    runs = stats_module.load_runs(paths)
    output = {
        FORMAT_MARKDOWN: stats_module.render_markdown,
        FORMAT_JSON: stats_module.render_json,
        KEY_CSV: stats_module.render_csv,
    }[FORMAT_JSON if args.json else args.format](runs)
    print(output, end=EMPTY_STRING if output.endswith(NEWLINE) else NEWLINE)
    if args.budget is not None:
        total = stats_module.aggregate_totals(runs)[KEY_COST]
        if total > args.budget:
            print(TEMPLATE_BUDGET_EXCEEDED_6F_6F.format(total, args.budget), file=sys.stderr)
            return 1
    return 0


def _command_pilot(args: argparse.Namespace) -> int:
    root = resolve_repository_root(args)
    if args.pilot_command == COMMAND_LIST:
        pilots = pilot_module.list_pilots(root)
        if args.json:
            emit_payload({KEY_PILOTS: pilots}, True)
        else:
            for pilot in pilots:
                print(TEMPLATE_20_22.format(pilot[KEY_NAME], pilot[KEY_STACK], pilot[KEY_COMMIT][:12], pilot[KEY_FOCUS]))
        return 0
    result = pilot_module.run_pilot(
        root=root,
        name=args.name,
        workspace=Path(args.workspace).expanduser() if args.workspace else None,
        prompt=args.prompt,
        verify_command=args.verify,
        profile=args.profile,
        keep=args.keep,
        dry_run=args.dry_run,
        model=os.environ.get(TEXT_OPENCODE_PILOT_MODEL),
        agent=args.agent,
        setup_command=args.setup,
    )
    if args.json:
        emit_payload(result, True)
    elif result.get(KEY_DRY_RUN):
        print(TEMPLATE_PILOT.format(result[COMMAND_PILOT]))
        print(TEMPLATE_WORKSPACE.format(result[KEY_WORKSPACE]))
        for step in result[KEY_STEPS]:
            print(TEMPLATE_TEMPLATE.format(step))
    else:
        print(TEMPLATE_PILOT.format(result[COMMAND_PILOT]))
        print(TEMPLATE_OPENCODE_EXIT.format(result[KEY_OPENCODE_EXIT]))
        print(TEMPLATE_VERIFICATION_EXIT.format(result[KEY_VERIFICATION_EXIT]))
        print(TEMPLATE_SUCCESS.format(result[KEY_SUCCESS]))
        print(TEMPLATE_COST_6F.format(result[KEY_COST]))
        print(TEMPLATE_ARTIFACTS_ARTIFACTS.format(result[KEY_WORKSPACE]))
    if result.get(KEY_DRY_RUN):
        return 0
    return 0 if result.get(KEY_SUCCESS) else 1
