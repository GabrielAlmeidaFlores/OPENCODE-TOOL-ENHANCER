"""
Unit tests for cost and token reporting.
"""
from __future__ import annotations

import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from tests import support

from ote_cli import stats
from ote_cli.paths import OteError


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
    (run / "meta.json").write_text(
        json.dumps(
            {
                "run_id": name,
                "arm": arm,
                "task_id": task,
                "model": "provider/model",
                "agent": "coordinator",
                "working_directory": ".",
                "wall_time_seconds": 12,
                "verification_exit": 0,
            }
        ),
        encoding="utf-8",
    )
    events = [
        {
            "type": "step_finish",
            "part": {
                "cost": cost,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "reasoning": 1,
                    "cache": {"read": 2, "write": 3},
                },
            },
        },
        {"type": "tool_use", "part": {"tool": "read"}},
        {"type": "tool_use", "part": {"tool": "bash", "state": {"status": "error" if tool_error else "completed"}}},
    ]
    (run / "session.jsonl").write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")
    return run


class ParseTests(unittest.TestCase):

    def test_parse_session_sums_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = write_run(Path(directory), "run-1", "baseline", "task", 0.5, 100, 20, tool_error=True)
            session_totals = stats.parse_session(run / "session.jsonl")
            self.assertAlmostEqual(session_totals["cost"], 0.5)
            self.assertEqual(session_totals["input_tokens"], 100)
            self.assertEqual(session_totals["output_tokens"], 20)
            self.assertEqual(session_totals["steps"], 1)
            self.assertEqual(session_totals["tool_calls"], 2)
            self.assertEqual(session_totals["tool_errors"], 1)
            self.assertEqual(session_totals["tool_counts"]["read"], 1)

    def test_missing_session_returns_zeros(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            session_totals = stats.parse_session(Path(directory) / "missing.jsonl")
            self.assertEqual(session_totals["cost"], 0.0)
            self.assertEqual(session_totals["steps"], 0)

    def test_file_path_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "meta.json"
            path.write_text("{}", encoding="utf-8")
            self.assertEqual(stats.load_runs([path]), [])

    def test_malformed_session_lines_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session.jsonl"
            path.write_text("not json\n[]\n", encoding="utf-8")
            session_totals = stats.parse_session(path)
            self.assertEqual(session_totals["steps"], 0)

    def test_summarize_run_reads_meta(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = write_run(Path(directory), "run-1", "baseline", "task", 0.5, 100, 20)
            summary = stats.summarize_run(run)
            self.assertIsNotNone(summary)
            self.assertEqual(summary.arm, "baseline")
            self.assertEqual(summary.wall_time_seconds, 12)
            self.assertEqual(summary.verification_exit, 0)

    def test_invalid_meta_raises(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory) / "run"
            run.mkdir()
            (run / "meta.json").write_text("{", encoding="utf-8")
            with self.assertRaises(OteError):
                stats.summarize_run(run)

    def test_load_runs_accepts_parent_and_run_directories(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_run(root, "a", "baseline", "task", 0.1, 1, 1)
            write_run(root, "b", "optimized", "task", 0.2, 2, 2)
            self.assertEqual(len(stats.load_runs([root])), 2)
            self.assertEqual(len(stats.load_runs([root / "a"])), 1)


class RenderTests(unittest.TestCase):

    def _runs(self) -> list[stats.RunSummary]:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        write_run(root, "baseline", "baseline", "task", 1.0, 1000, 100)
        write_run(root, "optimized", "optimized", "task", 0.5, 500, 50)
        return stats.load_runs([root])

    def test_markdown_contains_summary_and_comparison(self) -> None:
        rendered = stats.render_markdown(self._runs())
        self.assertIn("# Cost and Token Report", rendered)
        self.assertIn("Baseline vs optimized", rendered)
        self.assertIn("0.500", rendered)
        self.assertIn("By agent", rendered)

    def test_json_totals(self) -> None:
        payload = json.loads(stats.render_json(self._runs()))
        self.assertEqual(payload["totals"]["runs"], 2)
        self.assertAlmostEqual(payload["totals"]["cost"], 1.5)
        self.assertEqual(len(payload["comparison"]), 1)

    def test_csv_header_and_rows(self) -> None:
        rendered = stats.render_csv(self._runs())
        lines = rendered.strip().splitlines()
        self.assertIn("run_id,arm", lines[0])
        self.assertEqual(len(lines), 3)

    def test_csv_quotes_commas(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_run(root, "run,one", "baseline", "task", 0.1, 1, 1)
            runs = stats.load_runs([root])
            rendered = stats.render_csv(runs)
            rows = list(csv.reader(io.StringIO(rendered)))
            self.assertEqual(rows[1][0], "run,one")

    def test_empty_report(self) -> None:
        self.assertIn("No completed result directories", stats.render_markdown([]))
        self.assertEqual(json.loads(stats.render_json([]))["totals"]["runs"], 0)


class ComparisonTests(unittest.TestCase):

    def test_comparison_ratios(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_run(root, "baseline", "baseline", "task", 1.0, 1000, 100)
            write_run(root, "optimized", "optimized", "task", 0.5, 500, 50)
            comparison = stats.compare_arms(stats.load_runs([root]))
            self.assertEqual(len(comparison), 1)
            self.assertAlmostEqual(comparison[0]["cost_ratio"], 0.5)
            self.assertAlmostEqual(comparison[0]["token_ratio"], 0.5)
            self.assertEqual(comparison[0]["baseline_pass_rate"], 1.0)
            self.assertEqual(comparison[0]["baseline_runs"], 1)

    def test_comparison_averages_multiple_runs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_run(root, "baseline-1", "baseline", "task", 1.0, 100, 10)
            write_run(root, "baseline-2", "baseline", "task", 2.0, 200, 30)
            write_run(root, "optimized-1", "optimized", "task", 0.5, 50, 5)
            write_run(root, "optimized-2", "optimized", "task", 1.0, 100, 15)
            comparison = stats.compare_arms(stats.load_runs([root]))
            self.assertEqual(len(comparison), 1)
            self.assertEqual(comparison[0]["baseline_runs"], 2)
            self.assertEqual(comparison[0]["optimized_runs"], 2)
            self.assertAlmostEqual(comparison[0]["baseline_cost"], 1.5)
            self.assertAlmostEqual(comparison[0]["optimized_cost"], 0.75)
            self.assertAlmostEqual(comparison[0]["cost_ratio"], 0.5)
            self.assertAlmostEqual(comparison[0]["token_ratio"], 0.5)

    def test_no_comparison_without_both_arms(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_run(root, "baseline", "baseline", "task", 1.0, 10, 10)
            self.assertEqual(stats.compare_arms(stats.load_runs([root])), [])


if __name__ == "__main__":
    unittest.main()
