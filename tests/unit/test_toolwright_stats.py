"""
Unit tests for cost and token reporting.
"""
from __future__ import annotations
from tests.unit.test_toolwright_stats_strings import (
    KEY_A,
    KEY_AGENT,
    KEY_ARM,
    KEY_B,
    KEY_BASELINE,
    KEY_BASELINE_COST,
    KEY_BASELINE_PASS_RATE,
    KEY_BASELINE_RUNS,
    KEY_BASH,
    KEY_CACHE,
    KEY_COMPARISON,
    KEY_COMPLETED,
    KEY_COORDINATOR,
    KEY_COST,
    KEY_COST_RATIO,
    KEY_ERROR,
    KEY_INPUT,
    KEY_INPUT_TOKENS,
    KEY_MODEL,
    KEY_OPTIMIZED,
    KEY_OPTIMIZED_COST,
    KEY_OPTIMIZED_RUNS,
    KEY_OUTPUT,
    KEY_OUTPUT_TOKENS,
    KEY_PART,
    KEY_READ,
    KEY_REASONING,
    KEY_RUN,
    KEY_RUNS,
    KEY_RUN_ID,
    KEY_STATE,
    KEY_STATUS,
    KEY_STEPS,
    KEY_STEP_FINISH,
    KEY_TASK,
    KEY_TASK_ID,
    KEY_TOKENS,
    KEY_TOKEN_RATIO,
    KEY_TOOL,
    KEY_TOOL_CALLS,
    KEY_TOOL_COUNTS,
    KEY_TOOL_ERRORS,
    KEY_TOOL_USE,
    KEY_TOTALS,
    KEY_TYPE,
    KEY_VERIFICATION_EXIT,
    KEY_WALL_TIME_SECONDS,
    KEY_WORKING_DIRECTORY,
    KEY_WRITE,
    TEXT_0_500,
    TEXT_BASELINE_1,
    TEXT_BASELINE_2,
    TEXT_BASELINE_VS_OPTIMIZED,
    TEXT_BY_AGENT,
    TEXT_COST_AND_TOKEN_REPORT,
    TEXT_MAIN,
    TEXT_META_JSON,
    TEXT_MISSING_JSONL,
    TEXT_NOT_JSON,
    TEXT_NO_COMPLETED_RESULT_DIRECTORIES,
    TEXT_OPTIMIZED_1,
    TEXT_OPTIMIZED_2,
    TEXT_PROVIDER_MODEL,
    TEXT_RUN_1,
    TEXT_RUN_ID_ARM,
    TEXT_RUN_ONE,
    TEXT_SESSION_JSONL,
    TEXT_TEXT,
    TEXT_TEXT_2,
    TEXT_TEXT_3,
    TEXT_TEXT_4,
    TEXT_UTF_8,
)

import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from tests import support

from toolwright_cli import stats
from toolwright_cli.paths import ToolWrightError


def write_run(
    root: Path,
    name: str,
    arm: str,
    task: str,
    cost: float,
    input_tokens: int,
    output_tokens: int,
    tool_error: bool = False,
) -> Path:
    run = root / name
    run.mkdir(parents=True)
    (run / TEXT_META_JSON).write_text(
        json.dumps(
            {
                KEY_RUN_ID: name,
                KEY_ARM: arm,
                KEY_TASK_ID: task,
                KEY_MODEL: TEXT_PROVIDER_MODEL,
                KEY_AGENT: KEY_COORDINATOR,
                KEY_WORKING_DIRECTORY: TEXT_TEXT,
                KEY_WALL_TIME_SECONDS: 12,
                KEY_VERIFICATION_EXIT: 0,
            }
        ),
        encoding=TEXT_UTF_8,
    )
    events = [
        {
            KEY_TYPE: KEY_STEP_FINISH,
            KEY_PART: {
                KEY_COST: cost,
                KEY_TOKENS: {
                    KEY_INPUT: input_tokens,
                    KEY_OUTPUT: output_tokens,
                    KEY_REASONING: 1,
                    KEY_CACHE: {KEY_READ: 2, KEY_WRITE: 3},
                },
            },
        },
        {KEY_TYPE: KEY_TOOL_USE, KEY_PART: {KEY_TOOL: KEY_READ}},
        {KEY_TYPE: KEY_TOOL_USE, KEY_PART: {KEY_TOOL: KEY_BASH, KEY_STATE: {KEY_STATUS: KEY_ERROR if tool_error else KEY_COMPLETED}}},
    ]
    (run / TEXT_SESSION_JSONL).write_text(TEXT_TEXT_2.join(json.dumps(event) for event in events) + TEXT_TEXT_2, encoding=TEXT_UTF_8)
    return run


class ParseTests(unittest.TestCase):

    def test_parse_session_sums_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = write_run(Path(directory), TEXT_RUN_1, KEY_BASELINE, KEY_TASK, 0.5, 100, 20, tool_error=True)
            session_totals = stats.parse_session(run / TEXT_SESSION_JSONL)
            self.assertAlmostEqual(session_totals[KEY_COST], 0.5)
            self.assertEqual(session_totals[KEY_INPUT_TOKENS], 100)
            self.assertEqual(session_totals[KEY_OUTPUT_TOKENS], 20)
            self.assertEqual(session_totals[KEY_STEPS], 1)
            self.assertEqual(session_totals[KEY_TOOL_CALLS], 2)
            self.assertEqual(session_totals[KEY_TOOL_ERRORS], 1)
            self.assertEqual(session_totals[KEY_TOOL_COUNTS][KEY_READ], 1)

    def test_missing_session_returns_zeros(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            session_totals = stats.parse_session(Path(directory) / TEXT_MISSING_JSONL)
            self.assertEqual(session_totals[KEY_COST], 0.0)
            self.assertEqual(session_totals[KEY_STEPS], 0)

    def test_file_path_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / TEXT_META_JSON
            path.write_text(TEXT_TEXT_3, encoding=TEXT_UTF_8)
            self.assertEqual(stats.load_runs([path]), [])

    def test_malformed_session_lines_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / TEXT_SESSION_JSONL
            path.write_text(TEXT_NOT_JSON, encoding=TEXT_UTF_8)
            session_totals = stats.parse_session(path)
            self.assertEqual(session_totals[KEY_STEPS], 0)

    def test_summarize_run_reads_meta(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = write_run(Path(directory), TEXT_RUN_1, KEY_BASELINE, KEY_TASK, 0.5, 100, 20)
            summary = stats.summarize_run(run)
            self.assertIsNotNone(summary)
            self.assertEqual(summary.arm, KEY_BASELINE)
            self.assertEqual(summary.wall_time_seconds, 12)
            self.assertEqual(summary.verification_exit, 0)

    def test_invalid_meta_raises(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / KEY_RUN
            run.mkdir()
            (run / TEXT_META_JSON).write_text(TEXT_TEXT_4, encoding=TEXT_UTF_8)
            with self.assertRaises(ToolWrightError):
                stats.summarize_run(run)

    def test_load_runs_accepts_parent_and_run_directories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_run(root, KEY_A, KEY_BASELINE, KEY_TASK, 0.1, 1, 1)
            write_run(root, KEY_B, KEY_OPTIMIZED, KEY_TASK, 0.2, 2, 2)
            self.assertEqual(len(stats.load_runs([root])), 2)
            self.assertEqual(len(stats.load_runs([root / KEY_A])), 1)


class RenderTests(unittest.TestCase):

    def _runs(self) -> list[stats.RunSummary]:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        write_run(root, KEY_BASELINE, KEY_BASELINE, KEY_TASK, 1.0, 1000, 100)
        write_run(root, KEY_OPTIMIZED, KEY_OPTIMIZED, KEY_TASK, 0.5, 500, 50)
        return stats.load_runs([root])

    def test_markdown_contains_summary_and_comparison(self) -> None:
        rendered = stats.render_markdown(self._runs())
        self.assertIn(TEXT_COST_AND_TOKEN_REPORT, rendered)
        self.assertIn(TEXT_BASELINE_VS_OPTIMIZED, rendered)
        self.assertIn(TEXT_0_500, rendered)
        self.assertIn(TEXT_BY_AGENT, rendered)

    def test_json_totals(self) -> None:
        payload = json.loads(stats.render_json(self._runs()))
        self.assertEqual(payload[KEY_TOTALS][KEY_RUNS], 2)
        self.assertAlmostEqual(payload[KEY_TOTALS][KEY_COST], 1.5)
        self.assertEqual(len(payload[KEY_COMPARISON]), 1)

    def test_csv_header_and_rows(self) -> None:
        rendered = stats.render_csv(self._runs())
        lines = rendered.strip().splitlines()
        self.assertIn(TEXT_RUN_ID_ARM, lines[0])
        self.assertEqual(len(lines), 3)

    def test_csv_quotes_commas(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_run(root, TEXT_RUN_ONE, KEY_BASELINE, KEY_TASK, 0.1, 1, 1)
            runs = stats.load_runs([root])
            rendered = stats.render_csv(runs)
            rows = list(csv.reader(io.StringIO(rendered)))
            self.assertEqual(rows[1][0], TEXT_RUN_ONE)

    def test_empty_report(self) -> None:
        self.assertIn(TEXT_NO_COMPLETED_RESULT_DIRECTORIES, stats.render_markdown([]))
        self.assertEqual(json.loads(stats.render_json([]))[KEY_TOTALS][KEY_RUNS], 0)


class ComparisonTests(unittest.TestCase):

    def test_comparison_ratios(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_run(root, KEY_BASELINE, KEY_BASELINE, KEY_TASK, 1.0, 1000, 100)
            write_run(root, KEY_OPTIMIZED, KEY_OPTIMIZED, KEY_TASK, 0.5, 500, 50)
            comparison = stats.compare_arms(stats.load_runs([root]))
            self.assertEqual(len(comparison), 1)
            self.assertAlmostEqual(comparison[0][KEY_COST_RATIO], 0.5)
            self.assertAlmostEqual(comparison[0][KEY_TOKEN_RATIO], 0.5)
            self.assertEqual(comparison[0][KEY_BASELINE_PASS_RATE], 1.0)
            self.assertEqual(comparison[0][KEY_BASELINE_RUNS], 1)

    def test_comparison_averages_multiple_runs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_run(root, TEXT_BASELINE_1, KEY_BASELINE, KEY_TASK, 1.0, 100, 10)
            write_run(root, TEXT_BASELINE_2, KEY_BASELINE, KEY_TASK, 2.0, 200, 30)
            write_run(root, TEXT_OPTIMIZED_1, KEY_OPTIMIZED, KEY_TASK, 0.5, 50, 5)
            write_run(root, TEXT_OPTIMIZED_2, KEY_OPTIMIZED, KEY_TASK, 1.0, 100, 15)
            comparison = stats.compare_arms(stats.load_runs([root]))
            self.assertEqual(len(comparison), 1)
            self.assertEqual(comparison[0][KEY_BASELINE_RUNS], 2)
            self.assertEqual(comparison[0][KEY_OPTIMIZED_RUNS], 2)
            self.assertAlmostEqual(comparison[0][KEY_BASELINE_COST], 1.5)
            self.assertAlmostEqual(comparison[0][KEY_OPTIMIZED_COST], 0.75)
            self.assertAlmostEqual(comparison[0][KEY_COST_RATIO], 0.5)
            self.assertAlmostEqual(comparison[0][KEY_TOKEN_RATIO], 0.5)

    def test_no_comparison_without_both_arms(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_run(root, KEY_BASELINE, KEY_BASELINE, KEY_TASK, 1.0, 10, 10)
            self.assertEqual(stats.compare_arms(stats.load_runs([root])), [])


if __name__ == TEXT_MAIN:
    unittest.main()
