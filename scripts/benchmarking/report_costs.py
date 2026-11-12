#!/usr/bin/env python3
"""
Aggregate benchmark artifacts into a Markdown cost and token report.

The report reads each run directory under the results root, parses
session.jsonl and meta.json, and prints one row per run plus a summary.
It does not call a model and does not modify the results.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RunSummary:
    """
    Aggregated metrics for one benchmark run.
    """

    run_id: str
    arm: str
    task_id: str
    model: str
    agent: str
    working_directory: str
    cost: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    steps: int = 0
    tool_calls: int = 0
    wall_time_seconds: int = 0
    verification_exit: int | None = None
    files: list[str] = field(default_factory=list)


def parse_session(session_path: Path) -> dict[str, int | float]:
    """
    Sum cost, tokens, steps, and tool calls from a session JSONL file.
    """
    totals: dict[str, int | float] = {
        "cost": 0.0,
        "input_tokens": 0,
        "output_tokens": 0,
        "reasoning_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "steps": 0,
        "tool_calls": 0,
    }
    if not session_path.exists():
        return totals
    for line in session_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        part = event.get("part", {})
        if event.get("type") == "step_finish":
            totals["steps"] += 1
            totals["cost"] += float(part.get("cost") or 0.0)
            tokens = part.get("tokens", {})
            totals["input_tokens"] += int(tokens.get("input") or 0)
            totals["output_tokens"] += int(tokens.get("output") or 0)
            totals["reasoning_tokens"] += int(tokens.get("reasoning") or 0)
            cache = tokens.get("cache", {})
            totals["cache_read_tokens"] += int(cache.get("read") or 0)
            totals["cache_write_tokens"] += int(cache.get("write") or 0)
        if event.get("type") == "tool_use":
            totals["tool_calls"] += 1
    return totals


def summarize_run(run_dir: Path) -> RunSummary | None:
    """
    Build a RunSummary from one result directory, or return None when meta is missing.
    """
    meta_path = run_dir / "meta.json"
    if not meta_path.exists():
        return None
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    summary = RunSummary(
        run_id=str(meta.get("run_id", run_dir.name)),
        arm=str(meta.get("arm", "unknown")),
        task_id=str(meta.get("task_id", "unknown")),
        model=str(meta.get("model", "unknown")),
        agent=str(meta.get("agent", "unknown")),
        working_directory=str(meta.get("working_directory", ".")),
        wall_time_seconds=int(meta.get("wall_time_seconds") or 0),
        verification_exit=meta.get("verification_exit"),
    )
    totals = parse_session(run_dir / "session.jsonl")
    summary.cost = float(totals["cost"])
    summary.input_tokens = int(totals["input_tokens"])
    summary.output_tokens = int(totals["output_tokens"])
    summary.reasoning_tokens = int(totals["reasoning_tokens"])
    summary.cache_read_tokens = int(totals["cache_read_tokens"])
    summary.cache_write_tokens = int(totals["cache_write_tokens"])
    summary.steps = int(totals["steps"])
    summary.tool_calls = int(totals["tool_calls"])
    return summary


def render_report(runs: list[RunSummary]) -> str:
    """
    Render a Markdown report for the provided runs.
    """
    if not runs:
        return "# Benchmark Cost Report\n\nNo completed result directories were found.\n"
    lines = [
        "# Benchmark Cost Report",
        "",
        "| Run | Arm | Task | Model | Cost | Input | Output | Steps | Tools | Wall | Verify |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for run in runs:
        verify = "n/a" if run.verification_exit is None else str(run.verification_exit)
        lines.append(
            f"| {run.run_id} | {run.arm} | {run.task_id} | {run.model} | "
            f"${run.cost:.6f} | {run.input_tokens} | {run.output_tokens} | "
            f"{run.steps} | {run.tool_calls} | {run.wall_time_seconds}s | {verify} |"
        )
    total_cost = sum(run.cost for run in runs)
    total_input = sum(run.input_tokens for run in runs)
    total_output = sum(run.output_tokens for run in runs)
    passed = sum(1 for run in runs if run.verification_exit == 0)
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Runs: {len(runs)}",
            f"- Verification passed: {passed}/{len(runs)}",
            f"- Total cost: ${total_cost:.6f}",
            f"- Input tokens: {total_input}",
            f"- Output tokens: {total_output}",
            "",
            "Costs and tokens are summed from `session.jsonl` step-finish events. "
            "`opencode stats` can return zero for ephemeral projects, so it is not used as the primary source.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    """
    Parse arguments, aggregate runs, and print the report.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "benchmarks/results",
        help="directory containing run result directories",
    )
    args = parser.parse_args()
    runs = [summary for path in sorted(args.results.iterdir()) if path.is_dir() for summary in [summarize_run(path)] if summary]
    print(render_report(runs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
