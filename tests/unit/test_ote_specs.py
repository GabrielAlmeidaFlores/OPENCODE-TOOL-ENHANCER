"""
Unit tests for the spec-driven workflow.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests import support

from ote_cli import specs
from ote_cli.paths import OteError


class SpecTestCase(unittest.TestCase):
    """
    Base class providing a temporary repository root.
    """

    def setUp(self) -> None:
        """
        Create a temporary root.
        """
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)


class CreateTests(SpecTestCase):
    """
    Tests for creating artifacts.
    """

    def test_create_with_criteria(self) -> None:
        """
        The four artifacts are created with the supplied criteria.
        """
        directory = specs.create(self.root, "User Authentication", ["Reject weak passwords", "Return a session"])
        self.assertTrue(directory.is_dir())
        for name in specs.FILES:
            self.assertTrue((directory / name).is_file())
        requirements = (directory / "requirements.md").read_text(encoding="utf-8")
        self.assertIn("AC-1: Reject weak passwords", requirements)
        self.assertIn("AC-2: Return a session", requirements)

    def test_duplicate_spec_is_rejected(self) -> None:
        """
        Creating the same slug twice is refused.
        """
        specs.create(self.root, "Auth", ["One criterion"])
        with self.assertRaises(OteError):
            specs.create(self.root, "Auth", ["Another"])

    def test_placeholder_criterion_is_rejected(self) -> None:
        """
        A criterion containing an angle-bracket placeholder is refused.
        """
        with self.assertRaises(OteError):
            specs.create(self.root, "Auth", ["<describe behavior>"])

    def test_blank_feature_is_rejected(self) -> None:
        """
        A feature name without letters or digits is rejected.
        """
        with self.assertRaises(OteError):
            specs.create(self.root, "!!!", [])

    def test_list_specs_reports_missing_files(self) -> None:
        """
        An incomplete directory is reported.
        """
        directory = self.root / "specs/incomplete"
        directory.mkdir(parents=True)
        results = specs.list_specs(self.root)
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0]["complete"])
        self.assertEqual(len(results[0]["missing"]), 4)


class PlanTests(SpecTestCase):
    """
    Tests for criterion and task mapping.
    """

    def _write(self, name: str, body: str) -> None:
        """
        Write one spec artifact.
        """
        (self.root / "specs/demo" / name).write_text(body, encoding="utf-8")

    def test_fresh_spec_fails_plan(self) -> None:
        """
        Placeholder tasks do not satisfy the plan.
        """
        specs.create(self.root, "Demo", ["Works"])
        result = specs.plan(self.root, "demo")
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("no tasks" in issue for issue in result["issues"]))

    def test_valid_plan_passes(self) -> None:
        """
        A criterion with a mapped task passes.
        """
        specs.create(self.root, "Demo", ["Works"])
        self._write("tasks.md", "- [ ] T-1: Implement (criterion: AC-1)\n")
        result = specs.plan(self.root, "demo")
        self.assertEqual(result["status"], "ok")

    def test_unknown_criterion_fails(self) -> None:
        """
        A task referencing a missing criterion fails.
        """
        specs.create(self.root, "Demo", ["Works"])
        self._write("tasks.md", "- [ ] T-1: Implement (criterion: AC-9)\n")
        result = specs.plan(self.root, "demo")
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("AC-9" in issue for issue in result["issues"]))

    def test_uncovered_criterion_fails(self) -> None:
        """
        A criterion without a task fails.
        """
        specs.create(self.root, "Demo", ["One", "Two"])
        self._write("tasks.md", "- [ ] T-1: Implement (criterion: AC-1)\n")
        result = specs.plan(self.root, "demo")
        self.assertTrue(any("AC-2 has no task" in issue for issue in result["issues"]))


class VerifyTests(SpecTestCase):
    """
    Tests for evidence verification.
    """

    def _prepare(self, evidence: str) -> None:
        """
        Create a spec with a task and the supplied evidence.
        """
        specs.create(self.root, "Demo", ["Works"])
        (self.root / "specs/demo/tasks.md").write_text(
            "- [ ] T-1: Implement (criterion: AC-1)\n", encoding="utf-8"
        )
        (self.root / "specs/demo/evidence.md").write_text(evidence, encoding="utf-8")

    def test_missing_evidence_fails(self) -> None:
        """
        A criterion without evidence fails verification.
        """
        self._prepare("- AC-1: <command>\n")
        result = specs.verify(self.root, "demo")
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("AC-1 has no evidence" in issue for issue in result["issues"]))

    def test_valid_evidence_passes(self) -> None:
        """
        Matching evidence passes.
        """
        self._prepare("- AC-1: `npm test -- auth` passes\n")
        result = specs.verify(self.root, "demo")
        self.assertEqual(result["status"], "ok")

    def test_unknown_evidence_fails(self) -> None:
        """
        Evidence for a missing criterion fails.
        """
        self._prepare("- AC-9: something\n")
        result = specs.verify(self.root, "demo")
        self.assertTrue(any("unknown AC-9" in issue for issue in result["issues"]))

    def test_duplicate_evidence_fails(self) -> None:
        """
        Two evidence lines for one criterion are rejected.
        """
        self._prepare("- AC-1: one\n- AC-1: two\n")
        with self.assertRaises(OteError):
            specs.verify(self.root, "demo")

    def test_missing_artifact_is_an_error(self) -> None:
        """
        An incomplete spec directory raises a clear error.
        """
        (self.root / "specs/demo").mkdir(parents=True)
        with self.assertRaises(OteError):
            specs.verify(self.root, "demo")


if __name__ == "__main__":
    unittest.main()
