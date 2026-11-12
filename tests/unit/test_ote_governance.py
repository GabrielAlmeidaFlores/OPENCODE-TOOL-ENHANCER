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

    def test_all_agents_have_valid_contracts(self) -> None:
        results = governance.load_agent_contracts(support.REPO_ROOT)
        self.assertEqual(len(results), 12)
        failures = [result for result in results if result["status"] == "fail"]
        self.assertEqual(failures, [])

    def test_read_only_and_writer_roles(self) -> None:
        results = {result["agent"]: result for result in governance.load_agent_contracts(support.REPO_ROOT)}
        self.assertTrue(results["coordinator"]["read_only"])
        self.assertTrue(results["code-reviewer"]["denies_edit"])
        self.assertFalse(results["backend-developer"]["read_only"])
        self.assertIn("edit", results["backend-developer"]["allowed_actions"])

    def test_coordinator_is_primary(self) -> None:
        results = {result["agent"]: result for result in governance.load_agent_contracts(support.REPO_ROOT)}
        self.assertEqual(results["coordinator"]["mode"], "primary")


class BudgetTests(unittest.TestCase):

    def test_clean_record_is_allowed(self) -> None:
        record = {"iterations": 1, "tool_calls": 1, "writes": 1, "cost_usd": 0.1, "repeats": 0, "bounces": 0}
        result = governance.evaluate_record(record, SETTINGS)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["violations"], [])

    def test_budget_exceeded_blocks(self) -> None:
        result = governance.evaluate_record({"iterations": 11}, SETTINGS)
        self.assertFalse(result["allowed"])
        self.assertEqual(result["violations"][0]["kind"], "budget")

    def test_loop_detection_blocks(self) -> None:
        result = governance.evaluate_record({"repeats": 3}, SETTINGS)
        self.assertFalse(result["allowed"])
        self.assertEqual(result["violations"][0]["kind"], "loop")

    def test_deadlock_detection_blocks(self) -> None:
        result = governance.evaluate_record({"bounces": 4}, SETTINGS)
        self.assertFalse(result["allowed"])
        self.assertEqual(result["violations"][0]["kind"], "deadlock")

    def test_negative_record_value_is_rejected(self) -> None:
        with self.assertRaises(OteError):
            governance.evaluate_record({"iterations": -1}, SETTINGS)

    def test_defaults_apply_when_settings_are_missing(self) -> None:
        result = governance.evaluate_record({"iterations": 1}, {})
        self.assertTrue(result["allowed"])


class RiskGateTests(unittest.TestCase):

    def test_risk_levels(self) -> None:
        self.assertEqual(governance.required_gates_for_risk("low")["required"], ["verify"])
        self.assertIn("review", governance.required_gates_for_risk("medium")["required"])
        self.assertEqual(
            governance.required_gates_for_risk("high")["required"],
            ["verify", "review", "security"],
        )

    def test_unknown_risk_is_an_error(self) -> None:
        with self.assertRaises(OteError):
            governance.required_gates_for_risk("critical")


if __name__ == "__main__":
    unittest.main()
