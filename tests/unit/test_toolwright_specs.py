"""
Unit tests for the spec-driven workflow.
"""
from __future__ import annotations
from tests.unit.test_toolwright_specs_strings import (
    KEY_COMPLETE,
    KEY_DEMO,
    KEY_FAIL,
    KEY_ISSUES,
    KEY_MISSING,
    KEY_OK,
    KEY_STATUS,
    TEXT_AC_1_COMMAND,
    TEXT_AC_1_HAS_NO_EVIDENCE,
    TEXT_AC_1_NPM_TEST_AUTH_PASSES,
    TEXT_AC_1_ONE_AC_1_TWO,
    TEXT_AC_1_REJECT_WEAK_PASSWORDS,
    TEXT_AC_2_HAS_NO_TASK,
    TEXT_AC_2_RETURN_A_SESSION,
    TEXT_AC_9,
    TEXT_AC_9_SOMETHING,
    TEXT_ANOTHER,
    TEXT_AUTH,
    TEXT_DEMO,
    TEXT_DESCRIBE_BEHAVIOR,
    TEXT_MAIN,
    TEXT_NO_TASKS,
    TEXT_ONE,
    TEXT_ONE_CRITERION,
    TEXT_REJECT_WEAK_PASSWORDS,
    TEXT_REQUIREMENTS_MD,
    TEXT_RETURN_A_SESSION,
    TEXT_SPECS_DEMO,
    TEXT_SPECS_DEMO_EVIDENCE_MD,
    TEXT_SPECS_DEMO_TASKS_MD,
    TEXT_SPECS_INCOMPLETE,
    TEXT_TASKS_MD,
    TEXT_TEXT,
    TEXT_TWO,
    TEXT_T_1_IMPLEMENT_CRITERION_AC_1,
    TEXT_T_1_IMPLEMENT_CRITERION_AC_9,
    TEXT_UNKNOWN_AC_9,
    TEXT_USER_AUTHENTICATION,
    TEXT_UTF_8,
    TEXT_WORKS,
)

import tempfile
import unittest
from pathlib import Path

from tests import support

from toolwright_cli import specs
from toolwright_cli.paths import ToolWrightError


class SpecTestCase(unittest.TestCase):

    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)


class CreateTests(SpecTestCase):

    def test_create_with_criteria(self) -> None:
        directory = specs.create_spec_artifacts(self.root, TEXT_USER_AUTHENTICATION, [TEXT_REJECT_WEAK_PASSWORDS, TEXT_RETURN_A_SESSION])
        self.assertTrue(directory.is_dir())
        for name in specs.FILES:
            self.assertTrue((directory / name).is_file())
        requirements = (directory / TEXT_REQUIREMENTS_MD).read_text(encoding=TEXT_UTF_8)
        self.assertIn(TEXT_AC_1_REJECT_WEAK_PASSWORDS, requirements)
        self.assertIn(TEXT_AC_2_RETURN_A_SESSION, requirements)

    def test_duplicate_spec_is_rejected(self) -> None:
        specs.create_spec_artifacts(self.root, TEXT_AUTH, [TEXT_ONE_CRITERION])
        with self.assertRaises(ToolWrightError):
            specs.create_spec_artifacts(self.root, TEXT_AUTH, [TEXT_ANOTHER])

    def test_placeholder_criterion_is_rejected(self) -> None:
        with self.assertRaises(ToolWrightError):
            specs.create_spec_artifacts(self.root, TEXT_AUTH, [TEXT_DESCRIBE_BEHAVIOR])

    def test_blank_feature_is_rejected(self) -> None:
        with self.assertRaises(ToolWrightError):
            specs.create_spec_artifacts(self.root, TEXT_TEXT, [])

    def test_list_specs_reports_missing_files(self) -> None:
        directory = self.root / TEXT_SPECS_INCOMPLETE
        directory.mkdir(parents=True)
        results = specs.list_specs(self.root)
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0][KEY_COMPLETE])
        self.assertEqual(len(results[0][KEY_MISSING]), 4)


class PlanTests(SpecTestCase):

    def _write(self, name: str, body: str) -> None:
        (self.root / TEXT_SPECS_DEMO / name).write_text(body, encoding=TEXT_UTF_8)

    def test_fresh_spec_fails_plan(self) -> None:
        specs.create_spec_artifacts(self.root, TEXT_DEMO, [TEXT_WORKS])
        result = specs.validate_spec_plan(self.root, KEY_DEMO)
        self.assertEqual(result[KEY_STATUS], KEY_FAIL)
        self.assertTrue(any(TEXT_NO_TASKS in issue for issue in result[KEY_ISSUES]))

    def test_valid_plan_passes(self) -> None:
        specs.create_spec_artifacts(self.root, TEXT_DEMO, [TEXT_WORKS])
        self._write(TEXT_TASKS_MD, TEXT_T_1_IMPLEMENT_CRITERION_AC_1)
        result = specs.validate_spec_plan(self.root, KEY_DEMO)
        self.assertEqual(result[KEY_STATUS], KEY_OK)

    def test_unknown_criterion_fails(self) -> None:
        specs.create_spec_artifacts(self.root, TEXT_DEMO, [TEXT_WORKS])
        self._write(TEXT_TASKS_MD, TEXT_T_1_IMPLEMENT_CRITERION_AC_9)
        result = specs.validate_spec_plan(self.root, KEY_DEMO)
        self.assertEqual(result[KEY_STATUS], KEY_FAIL)
        self.assertTrue(any(TEXT_AC_9 in issue for issue in result[KEY_ISSUES]))

    def test_uncovered_criterion_fails(self) -> None:
        specs.create_spec_artifacts(self.root, TEXT_DEMO, [TEXT_ONE, TEXT_TWO])
        self._write(TEXT_TASKS_MD, TEXT_T_1_IMPLEMENT_CRITERION_AC_1)
        result = specs.validate_spec_plan(self.root, KEY_DEMO)
        self.assertTrue(any(TEXT_AC_2_HAS_NO_TASK in issue for issue in result[KEY_ISSUES]))


class VerifyTests(SpecTestCase):

    def _prepare(self, evidence: str) -> None:
        specs.create_spec_artifacts(self.root, TEXT_DEMO, [TEXT_WORKS])
        (self.root / TEXT_SPECS_DEMO_TASKS_MD).write_text(
            TEXT_T_1_IMPLEMENT_CRITERION_AC_1, encoding=TEXT_UTF_8
        )
        (self.root / TEXT_SPECS_DEMO_EVIDENCE_MD).write_text(evidence, encoding=TEXT_UTF_8)

    def test_missing_evidence_fails(self) -> None:
        self._prepare(TEXT_AC_1_COMMAND)
        result = specs.verify_spec_evidence(self.root, KEY_DEMO)
        self.assertEqual(result[KEY_STATUS], KEY_FAIL)
        self.assertTrue(any(TEXT_AC_1_HAS_NO_EVIDENCE in issue for issue in result[KEY_ISSUES]))

    def test_valid_evidence_passes(self) -> None:
        self._prepare(TEXT_AC_1_NPM_TEST_AUTH_PASSES)
        result = specs.verify_spec_evidence(self.root, KEY_DEMO)
        self.assertEqual(result[KEY_STATUS], KEY_OK)

    def test_unknown_evidence_fails(self) -> None:
        self._prepare(TEXT_AC_9_SOMETHING)
        result = specs.verify_spec_evidence(self.root, KEY_DEMO)
        self.assertTrue(any(TEXT_UNKNOWN_AC_9 in issue for issue in result[KEY_ISSUES]))

    def test_duplicate_evidence_fails(self) -> None:
        self._prepare(TEXT_AC_1_ONE_AC_1_TWO)
        with self.assertRaises(ToolWrightError):
            specs.verify_spec_evidence(self.root, KEY_DEMO)

    def test_missing_artifact_is_an_error(self) -> None:
        (self.root / TEXT_SPECS_DEMO).mkdir(parents=True)
        with self.assertRaises(ToolWrightError):
            specs.verify_spec_evidence(self.root, KEY_DEMO)


if __name__ == TEXT_MAIN:
    unittest.main()
