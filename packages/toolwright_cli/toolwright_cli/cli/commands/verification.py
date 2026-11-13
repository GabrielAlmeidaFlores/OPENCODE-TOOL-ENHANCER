"""
Verification, governance, and evaluation command handlers.

Public API: command handler functions used by :mod:`toolwright_cli.cli.main`.

Side effects: runs checks and prints results.
"""
from __future__ import annotations
from ..cli_strings import TEMPLATE_4_12, TEMPLATE_4_12_6_2F_S, TEMPLATE_4_22_8, TEMPLATE_ALLOWED, TEMPLATE_FAILURE_S, TEMPLATE_INVALID_JSON, TEMPLATE_PASSED_FAILED, TEMPLATE_RECORD_NOT_FOUND, TEMPLATE_REQUIRED, TEMPLATE_RISK, TEMPLATE_RUN_RECORD_MUST_BE_A_JSON_OBJECT, TEMPLATE_TEMPLATE_7, TEMPLATE_TEMPLATE_8, TEMPLATE_VALIDATOR_MODE
from ..cli_strings import (
    ENCODING_UTF8,
    KEY_AGENT,
    KEY_ALLOWED,
    KEY_CACHED,
    KEY_EXIT_CODE,
    KEY_FAILED,
    KEY_FAILURE_CLASS,
    KEY_GATE,
    KEY_KIND,
    KEY_MODE,
    KEY_PASSED,
    KEY_READ_ONLY,
    KEY_REQUIRED,
    KEY_RISK,
    KEY_SECONDS,
    KEY_STDERR,
    KEY_STDOUT,
    KEY_SUMMARY,
    KEY_VALIDATOR_MODE,
    KEY_VIOLATIONS,
    KEY_WRITER,
    TEXT_CACHED,
    TEXT_READ_ONLY,
)

import argparse
import json
from pathlib import Path

from ..common import emit_payload, resolve_repository_root
from ...constants import (
    KEY_DETAIL, KEY_FAILURES, KEY_ID, KEY_NAME, KEY_RESULTS, KEY_STATUS, NEWLINE,
    STATUS_FAIL, STATUS_OK,
)
from ...cli_constants import COMMAND_CONTRACTS, EMPTY_STRING
from ... import eval as eval_module
from ... import governance as governance_module
from ... import verify as verify_module
from ...paths import ToolWrightError

def _command_verify(args: argparse.Namespace) -> int:
    root = resolve_repository_root(args)
    config_path = None
    if args.config:
        candidate = Path(args.config).expanduser()
        config_path = candidate if candidate.is_absolute() else root / candidate
    checks, _ = verify_module.load_verification_config(root, config_path)
    results = verify_module.run_verification_checks(
        root,
        checks,
        only=args.only or None,
        use_cache=not args.no_cache,
    )
    summary = verify_module.summarize_results(results)
    if args.json:
        emit_payload(
            {
                KEY_RESULTS: [
                    {
                        KEY_NAME: result.name,
                        KEY_STATUS: result.status,
                        KEY_EXIT_CODE: result.exit_code,
                        KEY_SECONDS: result.seconds,
                        KEY_FAILURE_CLASS: result.failure_class,
                        KEY_CACHED: result.cached,
                        KEY_STDOUT: result.stdout,
                        KEY_STDERR: result.stderr,
                    }
                    for result in results
                ],
                KEY_SUMMARY: summary,
            },
            True,
        )
    else:
        for result in results:
            suffix = TEXT_CACHED if result.cached else EMPTY_STRING
            label = result.failure_class if result.status == STATUS_FAIL else STATUS_OK
            print(TEMPLATE_4_12_6_2F_S.format(result.status.upper(), result.name, result.seconds, label, suffix))
            if result.status == STATUS_FAIL:
                output = (result.stdout + NEWLINE + result.stderr).strip().splitlines()
                for line in output[-10:]:
                    print(TEMPLATE_TEMPLATE_8.format(line))
        print(TEMPLATE_PASSED_FAILED.format(summary[KEY_PASSED], summary[KEY_FAILED]))
    return 1 if summary[KEY_FAILED] else 0


def _command_govern(args: argparse.Namespace) -> int:
    root = resolve_repository_root(args)
    action = args.govern_command
    if action == COMMAND_CONTRACTS:
        results = governance_module.load_agent_contracts(root)
        failures = [result for result in results if result[KEY_STATUS] == STATUS_FAIL]
        if args.json:
            emit_payload({COMMAND_CONTRACTS: results, KEY_FAILURES: len(failures)}, True)
        else:
            for result in results:
                label = TEXT_READ_ONLY if result[KEY_READ_ONLY] else KEY_WRITER
                print(TEMPLATE_4_22_8.format(result[KEY_STATUS].upper(), result[KEY_AGENT], result[KEY_MODE], label))
                for violation in result[KEY_VIOLATIONS]:
                    print(TEMPLATE_TEMPLATE_8.format(violation))
            print(TEMPLATE_FAILURE_S.format(len(failures)))
        return 1 if failures else 0
    if action == KEY_GATE:
        gate = governance_module.required_gates_for_risk(args.risk)
        if args.json:
            emit_payload(gate, True)
        else:
            print(TEMPLATE_RISK.format(gate[KEY_RISK]))
            for requirement in gate[KEY_REQUIRED]:
                print(TEMPLATE_REQUIRED.format(requirement))
        return 0
    record_path = Path(args.record).expanduser()
    if not record_path.is_file():
        raise ToolWrightError(TEMPLATE_RECORD_NOT_FOUND.format(record_path))
    try:
        record = json.loads(record_path.read_text(encoding=ENCODING_UTF8))
    except json.JSONDecodeError as error:
        raise ToolWrightError(TEMPLATE_INVALID_JSON.format(record_path, error)) from error
    if not isinstance(record, dict):
        raise ToolWrightError(TEMPLATE_RUN_RECORD_MUST_BE_A_JSON_OBJECT.format(record_path))
    _, governance = verify_module.load_verification_config(root)
    evaluation = governance_module.evaluate_record(record, governance)
    if args.json:
        emit_payload(evaluation, True)
    else:
        print(TEMPLATE_ALLOWED.format(evaluation[KEY_ALLOWED]))
        print(TEMPLATE_VALIDATOR_MODE.format(evaluation[KEY_VALIDATOR_MODE]))
        for violation in evaluation[KEY_VIOLATIONS]:
            print(TEMPLATE_TEMPLATE_7.format(violation[KEY_KIND], violation[KEY_DETAIL]))
    return 0 if evaluation[KEY_ALLOWED] else 1


def _command_eval(args: argparse.Namespace) -> int:
    root = resolve_repository_root(args)
    results = eval_module.run_evaluation_cases(root, only=args.only or None)
    failures = [result for result in results if result[KEY_STATUS] == STATUS_FAIL]
    if args.json:
        emit_payload({KEY_RESULTS: results, KEY_FAILURES: len(failures)}, True)
    else:
        for result in results:
            print(TEMPLATE_4_12.format(result[KEY_STATUS].upper(), result[KEY_ID], result[KEY_DETAIL]))
        print(TEMPLATE_FAILURE_S.format(len(failures)))
    return 1 if failures else 0
