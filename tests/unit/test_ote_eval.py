"""
Unit tests for deterministic evaluation cases.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests import support

from ote_cli import eval as eval_module
from ote_cli.paths import OteError


class RepositoryEvalTests(unittest.TestCase):

    def test_all_cases_pass(self) -> None:
        results = eval_module.run_evaluation_cases(support.REPO_ROOT)
        self.assertEqual(len(results), 4)
        failures = [result for result in results if result["status"] == "fail"]
        self.assertEqual(failures, [])

    def test_only_selects_cases(self) -> None:
        results = eval_module.run_evaluation_cases(support.REPO_ROOT, only=["profiles"])
        self.assertEqual([result["id"] for result in results], ["profiles"])
        self.assertEqual(results[0]["status"], "ok")

    def test_unknown_case_is_an_error(self) -> None:
        with self.assertRaises(OteError):
            eval_module.run_evaluation_cases(support.REPO_ROOT, only=["nonsense"])


class EvalConfigTests(unittest.TestCase):

    def test_missing_cases_file_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(OteError):
                eval_module.load_cases(Path(directory))

    def test_unknown_case_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "tests/evals/cases.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"schema_version": 1, "cases": [{"id": "nope"}]}), encoding="utf-8")
            with self.assertRaises(OteError):
                eval_module.load_cases(root)

    def test_missing_catalog_is_a_failed_case(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cases = root / "tests/evals/cases.json"
            cases.parent.mkdir(parents=True)
            cases.write_text(
                json.dumps({"schema_version": 1, "cases": [{"id": "catalog"}]}),
                encoding="utf-8",
            )
            results = eval_module.run_evaluation_cases(root)
            self.assertEqual(results[0]["status"], "fail")
            self.assertIn("catalog", results[0]["detail"])

    def test_validator_failure_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cases = root / "tests/evals/cases.json"
            cases.parent.mkdir(parents=True)
            cases.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "cases": [{"id": "validator", "expected": {"exit_code": 0}}],
                    }
                ),
                encoding="utf-8",
            )
            script = root / "scripts/validation/validate_config.py"
            script.parent.mkdir(parents=True)
            script.write_text("raise SystemExit(1)\n", encoding="utf-8")
            results = eval_module.run_evaluation_cases(root)
            self.assertEqual(results[0]["status"], "fail")


if __name__ == "__main__":
    unittest.main()
