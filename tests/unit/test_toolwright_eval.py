"""
Unit tests for deterministic evaluation cases.
"""
from __future__ import annotations
from tests.unit.test_toolwright_eval_strings import (
    KEY_CASES,
    KEY_CATALOG,
    KEY_DETAIL,
    KEY_EXIT_CODE,
    KEY_EXPECTED,
    KEY_FAIL,
    KEY_ID,
    KEY_NONSENSE,
    KEY_NOPE,
    KEY_OK,
    KEY_PROFILES,
    KEY_SCHEMA_VERSION,
    KEY_STATUS,
    KEY_VALIDATOR,
    TEXT_MAIN,
    TEXT_RAISE_SYSTEMEXIT_1,
    TEXT_SCRIPTS_VALIDATION_VALIDATE_CONFIG_PY,
    TEXT_TESTS_EVALS_CASES_JSON,
    TEXT_UTF_8,
)

import json
import tempfile
import unittest
from pathlib import Path

from tests import support

from toolwright_cli import eval as eval_module
from toolwright_cli.paths import ToolWrightError


class RepositoryEvalTests(unittest.TestCase):

    def test_all_cases_pass(self) -> None:
        results = eval_module.run_evaluation_cases(support.REPO_ROOT)
        self.assertEqual(len(results), 4)
        failures = [result for result in results if result[KEY_STATUS] == KEY_FAIL]
        self.assertEqual(failures, [])

    def test_only_selects_cases(self) -> None:
        results = eval_module.run_evaluation_cases(support.REPO_ROOT, only=[KEY_PROFILES])
        self.assertEqual([result[KEY_ID] for result in results], [KEY_PROFILES])
        self.assertEqual(results[0][KEY_STATUS], KEY_OK)

    def test_unknown_case_is_an_error(self) -> None:
        with self.assertRaises(ToolWrightError):
            eval_module.run_evaluation_cases(support.REPO_ROOT, only=[KEY_NONSENSE])


class EvalConfigTests(unittest.TestCase):

    def test_missing_cases_file_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ToolWrightError):
                eval_module.load_cases(Path(directory))

    def test_unknown_case_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / TEXT_TESTS_EVALS_CASES_JSON
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({KEY_SCHEMA_VERSION: 1, KEY_CASES: [{KEY_ID: KEY_NOPE}]}), encoding=TEXT_UTF_8)
            with self.assertRaises(ToolWrightError):
                eval_module.load_cases(root)

    def test_missing_catalog_is_a_failed_case(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cases = root / TEXT_TESTS_EVALS_CASES_JSON
            cases.parent.mkdir(parents=True)
            cases.write_text(
                json.dumps({KEY_SCHEMA_VERSION: 1, KEY_CASES: [{KEY_ID: KEY_CATALOG}]}),
                encoding=TEXT_UTF_8,
            )
            results = eval_module.run_evaluation_cases(root)
            self.assertEqual(results[0][KEY_STATUS], KEY_FAIL)
            self.assertIn(KEY_CATALOG, results[0][KEY_DETAIL])

    def test_validator_failure_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cases = root / TEXT_TESTS_EVALS_CASES_JSON
            cases.parent.mkdir(parents=True)
            cases.write_text(
                json.dumps(
                    {
                        KEY_SCHEMA_VERSION: 1,
                        KEY_CASES: [{KEY_ID: KEY_VALIDATOR, KEY_EXPECTED: {KEY_EXIT_CODE: 0}}],
                    }
                ),
                encoding=TEXT_UTF_8,
            )
            script = root / TEXT_SCRIPTS_VALIDATION_VALIDATE_CONFIG_PY
            script.parent.mkdir(parents=True)
            script.write_text(TEXT_RAISE_SYSTEMEXIT_1, encoding=TEXT_UTF_8)
            results = eval_module.run_evaluation_cases(root)
            self.assertEqual(results[0][KEY_STATUS], KEY_FAIL)


if __name__ == TEXT_MAIN:
    unittest.main()
