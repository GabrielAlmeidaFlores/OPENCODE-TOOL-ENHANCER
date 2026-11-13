"""
Unit tests for the spec-driven workflow.
"""
from __future__ import annotations

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
        directory = specs.create_spec_artifacts(self.root, "User Authentication", ["Reject weak passwords", "Return a session"])
        self.assertTrue(directory.is_dir())
        for name in specs.FILES:
            self.assertTrue((directory / name).is_file())
        requirements = (directory / "requirements.md").read_text(encoding="utf-8")
        self.assertIn("AC-1: Reject weak passwords", requirements)
        self.assertIn("AC-2: Return a session", requirements)

    def test_duplicate_spec_is_rejected(self) -> None:
        specs.create_spec_artifacts(self.root, "Auth", ["One criterion"])
        with self.assertRaises(ToolWrightError):
            specs.create_spec_artifacts(self.root, "Auth", ["Another"])

    def test_placeholder_criterion_is_rejected(self) -> None:
        with self.assertRaises(ToolWrightError):
            specs.create_spec_artifacts(self.root, "Auth", ["<describe behavior>"])

    def test_blank_feature_is_rejected(self) -> None:
        with self.assertRaises(ToolWrightError):
            specs.create_spec_artifacts(self.root, "!!!", [])

    def test_list_specs_reports_missing_files(self) -> None:
        directory = self.root / "specs/incomplete"
        directory.mkdir(parents=True)
        results = specs.list_specs(self.root)
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0]["complete"])
        self.assertEqual(len(results[0]["missing"]), 4)


class PlanTests(SpecTestCase):

    def _write(self, name: str, body: str) -> None:
        (self.root / "specs/demo" / name).write_text(body, encoding="utf-8")

    def test_fresh_spec_fails_plan(self) -> None:
        specs.create_spec_artifacts(self.root, "Demo", ["Works"])
        result = specs.validate_spec_plan(self.root, "demo")
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("no tasks" in issue for issue in result["issues"]))

    def test_valid_plan_passes(self) -> None:
        specs.create_spec_artifacts(self.root, "Demo", ["Works"])
        self._write("tasks.md", "- [ ] T-1: Implement (criterion: AC-1)\n")
        result = specs.validate_spec_plan(self.root, "demo")
        self.assertEqual(result["status"], "ok")

    def test_unknown_criterion_fails(self) -> None:
        specs.create_spec_artifacts(self.root, "Demo", ["Works"])
        self._write("tasks.md", "- [ ] T-1: Implement (criterion: AC-9)\n")
        result = specs.validate_spec_plan(self.root, "demo")
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("AC-9" in issue for issue in result["issues"]))

    def test_uncovered_criterion_fails(self) -> None:
        specs.create_spec_artifacts(self.root, "Demo", ["One", "Two"])
        self._write("tasks.md", "- [ ] T-1: Implement (criterion: AC-1)\n")
        result = specs.validate_spec_plan(self.root, "demo")
        self.assertTrue(any("AC-2 has no task" in issue for issue in result["issues"]))


class VerifyTests(SpecTestCase):

    def _prepare(self, evidence: str) -> None:
        specs.create_spec_artifacts(self.root, "Demo", ["Works"])
        (self.root / "specs/demo/tasks.md").write_text(
            "- [ ] T-1: Implement (criterion: AC-1)\n", encoding="utf-8"
        )
        (self.root / "specs/demo/evidence.md").write_text(evidence, encoding="utf-8")

    def test_missing_evidence_fails(self) -> None:
        self._prepare("- AC-1: <command>\n")
        result = specs.verify_spec_evidence(self.root, "demo")
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("AC-1 has no evidence" in issue for issue in result["issues"]))

    def test_valid_evidence_passes(self) -> None:
        self._prepare("- AC-1: `npm test -- auth` passes\n")
        result = specs.verify_spec_evidence(self.root, "demo")
        self.assertEqual(result["status"], "ok")

    def test_unknown_evidence_fails(self) -> None:
        self._prepare("- AC-9: something\n")
        result = specs.verify_spec_evidence(self.root, "demo")
        self.assertTrue(any("unknown AC-9" in issue for issue in result["issues"]))

    def test_duplicate_evidence_fails(self) -> None:
        self._prepare("- AC-1: one\n- AC-1: two\n")
        with self.assertRaises(ToolWrightError):
            specs.verify_spec_evidence(self.root, "demo")

    def test_missing_artifact_is_an_error(self) -> None:
        (self.root / "specs/demo").mkdir(parents=True)
        with self.assertRaises(ToolWrightError):
            specs.verify_spec_evidence(self.root, "demo")


if __name__ == "__main__":
    unittest.main()
