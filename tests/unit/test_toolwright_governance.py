"""
Unit tests for governance contracts, budgets, and risk gates.
"""
from __future__ import annotations
from tests.unit.test_toolwright_governance_strings import (
    KEY_AGENT,
    KEY_ALLOWED,
    KEY_ALLOWED_ACTIONS,
    KEY_BOUNCES,
    KEY_BUDGET,
    KEY_COORDINATOR,
    KEY_COST_USD,
    KEY_CRITICAL,
    KEY_DEADLOCK,
    KEY_DENIES_EDIT,
    KEY_EDIT,
    KEY_FAIL,
    KEY_HIGH,
    KEY_ITERATIONS,
    KEY_KIND,
    KEY_LOOP,
    KEY_LOW,
    KEY_MAX_BOUNCES,
    KEY_MAX_COST_USD,
    KEY_MAX_DELEGATION_DEPTH,
    KEY_MAX_ITERATIONS,
    KEY_MAX_REPEATS,
    KEY_MAX_TOOL_CALLS,
    KEY_MAX_WRITES,
    KEY_MEDIUM,
    KEY_MODE,
    KEY_PRIMARY,
    KEY_READ_ONLY,
    KEY_REPEATS,
    KEY_REQUIRED,
    KEY_REVIEW,
    KEY_SECURITY,
    KEY_STATUS,
    KEY_TOOL_CALLS,
    KEY_VERIFY,
    KEY_VIOLATIONS,
    KEY_WRITES,
    TEXT_BACKEND_DEVELOPER,
    TEXT_CODE_REVIEWER,
    TEXT_MAIN,
)

import unittest

from tests import support

from toolwright_cli import governance
from toolwright_cli.paths import ToolWrightError

SETTINGS = {
    KEY_MAX_ITERATIONS: 10,
    KEY_MAX_TOOL_CALLS: 20,
    KEY_MAX_WRITES: 5,
    KEY_MAX_COST_USD: 1.0,
    KEY_MAX_DELEGATION_DEPTH: 2,
    KEY_MAX_REPEATS: 2,
    KEY_MAX_BOUNCES: 3,
}


class ContractTests(unittest.TestCase):

    def test_all_agents_have_valid_contracts(self) -> None:
        results = governance.load_agent_contracts(support.REPO_ROOT)
        self.assertEqual(len(results), 12)
        failures = [result for result in results if result[KEY_STATUS] == KEY_FAIL]
        self.assertEqual(failures, [])

    def test_read_only_and_writer_roles(self) -> None:
        results = {result[KEY_AGENT]: result for result in governance.load_agent_contracts(support.REPO_ROOT)}
        self.assertTrue(results[KEY_COORDINATOR][KEY_READ_ONLY])
        self.assertTrue(results[TEXT_CODE_REVIEWER][KEY_DENIES_EDIT])
        self.assertFalse(results[TEXT_BACKEND_DEVELOPER][KEY_READ_ONLY])
        self.assertIn(KEY_EDIT, results[TEXT_BACKEND_DEVELOPER][KEY_ALLOWED_ACTIONS])

    def test_coordinator_is_primary(self) -> None:
        results = {result[KEY_AGENT]: result for result in governance.load_agent_contracts(support.REPO_ROOT)}
        self.assertEqual(results[KEY_COORDINATOR][KEY_MODE], KEY_PRIMARY)


class BudgetTests(unittest.TestCase):

    def test_clean_record_is_allowed(self) -> None:
        record = {KEY_ITERATIONS: 1, KEY_TOOL_CALLS: 1, KEY_WRITES: 1, KEY_COST_USD: 0.1, KEY_REPEATS: 0, KEY_BOUNCES: 0}
        result = governance.evaluate_record(record, SETTINGS)
        self.assertTrue(result[KEY_ALLOWED])
        self.assertEqual(result[KEY_VIOLATIONS], [])

    def test_budget_exceeded_blocks(self) -> None:
        result = governance.evaluate_record({KEY_ITERATIONS: 11}, SETTINGS)
        self.assertFalse(result[KEY_ALLOWED])
        self.assertEqual(result[KEY_VIOLATIONS][0][KEY_KIND], KEY_BUDGET)

    def test_loop_detection_blocks(self) -> None:
        result = governance.evaluate_record({KEY_REPEATS: 3}, SETTINGS)
        self.assertFalse(result[KEY_ALLOWED])
        self.assertEqual(result[KEY_VIOLATIONS][0][KEY_KIND], KEY_LOOP)

    def test_deadlock_detection_blocks(self) -> None:
        result = governance.evaluate_record({KEY_BOUNCES: 4}, SETTINGS)
        self.assertFalse(result[KEY_ALLOWED])
        self.assertEqual(result[KEY_VIOLATIONS][0][KEY_KIND], KEY_DEADLOCK)

    def test_negative_record_value_is_rejected(self) -> None:
        with self.assertRaises(ToolWrightError):
            governance.evaluate_record({KEY_ITERATIONS: -1}, SETTINGS)

    def test_defaults_apply_when_settings_are_missing(self) -> None:
        result = governance.evaluate_record({KEY_ITERATIONS: 1}, {})
        self.assertTrue(result[KEY_ALLOWED])


class RiskGateTests(unittest.TestCase):

    def test_risk_levels(self) -> None:
        self.assertEqual(governance.required_gates_for_risk(KEY_LOW)[KEY_REQUIRED], [KEY_VERIFY])
        self.assertIn(KEY_REVIEW, governance.required_gates_for_risk(KEY_MEDIUM)[KEY_REQUIRED])
        self.assertEqual(
            governance.required_gates_for_risk(KEY_HIGH)[KEY_REQUIRED],
            [KEY_VERIFY, KEY_REVIEW, KEY_SECURITY],
        )

    def test_unknown_risk_is_an_error(self) -> None:
        with self.assertRaises(ToolWrightError):
            governance.required_gates_for_risk(KEY_CRITICAL)


if __name__ == TEXT_MAIN:
    unittest.main()
