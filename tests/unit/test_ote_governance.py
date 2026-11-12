"""
Unit tests for governance contracts, budgets, and risk gates.
"""
from __future__ import annotations

import unittest

from tests import support

from ote_cli import governance
from ote_cli.paths import OteError

SETTINGS = {
    "max_iterations": 10,
    "max_tool_calls": 20,
    "max_writes": 5,
    "max_cost_usd": 1.0,
    "max_delegation_depth": 2,
    "max_repeats": 2,
    "max_bounces": 3,
}


class ContractTests(unittest.TestCase):
    """
    Tests against the committed agent permissions.
    """

    def test_all_agents_have_valid_contracts(self) -> None:
        """
        Every agent contract reports no violations.
        """
        results = governance.contracts(support.REPO_ROOT)
        self.assertEqual(len(results), 12)
        failures = [result for result in results if result["status"] == "fail"]
        self.assertEqual(failures, [])

    def test_read_only_and_writer_roles(self) -> None:
        """
        Read-only roles deny edit and writer roles allow it.
        """
        results = {result["agent"]: result for result in governance.contracts(support.REPO_ROOT)}
        self.assertTrue(results["coordinator"]["read_only"])
        self.assertTrue(results["code-reviewer"]["denies_edit"])
        self.assertFalse(results["backend-developer"]["read_only"])
        self.assertIn("edit", results["backend-developer"]["allowed_actions"])

    def test_coordinator_is_primary(self) -> None:
        """
        The coordinator contract requires primary mode.
        """
        results = {result["agent"]: result for result in governance.contracts(support.REPO_ROOT)}
        self.assertEqual(results["coordinator"]["mode"], "primary")


class BudgetTests(unittest.TestCase):
    """
    Tests for budget, loop, and deadlock evaluation.
    """

    def test_clean_record_is_allowed(self) -> None:
        """
        A record inside every limit passes.
        """
        record = {"iterations": 1, "tool_calls": 1, "writes": 1, "cost_usd": 0.1, "repeats": 0, "bounces": 0}
        result = governance.evaluate_record(record, SETTINGS)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["violations"], [])

    def test_budget_exceeded_blocks(self) -> None:
        """
        Exceeding a budget produces a budget violation.
        """
        result = governance.evaluate_record({"iterations": 11}, SETTINGS)
        self.assertFalse(result["allowed"])
        self.assertEqual(result["violations"][0]["kind"], "budget")

    def test_loop_detection_blocks(self) -> None:
        """
        Repeated actions above the threshold are a loop.
        """
        result = governance.evaluate_record({"repeats": 3}, SETTINGS)
        self.assertFalse(result["allowed"])
        self.assertEqual(result["violations"][0]["kind"], "loop")

    def test_deadlock_detection_blocks(self) -> None:
        """
        Handoff bounces above the threshold are a deadlock.
        """
        result = governance.evaluate_record({"bounces": 4}, SETTINGS)
        self.assertFalse(result["allowed"])
        self.assertEqual(result["violations"][0]["kind"], "deadlock")

    def test_negative_record_value_is_rejected(self) -> None:
        """
        A negative counter is invalid input.
        """
        with self.assertRaises(OteError):
            governance.evaluate_record({"iterations": -1}, SETTINGS)

    def test_defaults_apply_when_settings_are_missing(self) -> None:
        """
        Missing settings fall back to the documented defaults.
        """
        result = governance.evaluate_record({"iterations": 1}, {})
        self.assertTrue(result["allowed"])


class RiskGateTests(unittest.TestCase):
    """
    Tests for risk-based gate selection.
    """

    def test_risk_levels(self) -> None:
        """
        Higher risk requires more gates.
        """
        self.assertEqual(governance.risk_gate("low")["required"], ["verify"])
        self.assertIn("review", governance.risk_gate("medium")["required"])
        self.assertEqual(
            governance.risk_gate("high")["required"],
            ["verify", "review", "security"],
        )

    def test_unknown_risk_is_an_error(self) -> None:
        """
        An unknown risk level is rejected.
        """
        with self.assertRaises(OteError):
            governance.risk_gate("critical")


if __name__ == "__main__":
    unittest.main()
