"""
Cost, token, and failure reporting for ``toolwright stats``.

Public API: :class:`RunSummary`, :func:`parse_session`, :func:`summarize_run`,
:func:`load_runs`, :func:`aggregate_totals`, :func:`compare_arms`, and the three render
functions.

Inputs are benchmark-style run directories containing ``meta.json`` and
``session.jsonl``. Reporting is local and file-based; nothing is uploaded.

Side effects: reads result directories only.
"""
from __future__ import annotations

import csv
import io
import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from .paths import ToolwrightError


@dataclass
class RunSummary:

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
    tool_errors: int = 0
    wall_time_seconds: int = 0
    verification_exit: int | None = None
    tool_counts: dict[str, int] = field(default_factory=dict)


def empty_session_totals() -> dict[str, Any]:
    return {
        "cost": 0.0,
        "input_tokens": 0,
        "output_tokens": 0,
        "reasoning_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
        "steps": 0,
        "tool_calls": 0,
        "tool_errors": 0,
        "tool_counts": Counter(),
    }


def parse_session(session_path: Path) -> dict[str, Any]:
    session_totals = empty_session_totals()
    if not session_path.is_file():
        return session_totals
    for line in session_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        part = event.get("part", {})
        if event.get("type") == "step_finish":
            session_totals["steps"] += 1
            session_totals["cost"] += float(part.get("cost") or 0.0)
            tokens = part.get("tokens", {})
            session_totals["input_tokens"] += int(tokens.get("input") or 0)
            session_totals["output_tokens"] += int(tokens.get("output") or 0)
            session_totals["reasoning_tokens"] += int(tokens.get("reasoning") or 0)
            cache = tokens.get("cache", {})
            session_totals["cache_read_tokens"] += int(cache.get("read") or 0)
            session_totals["cache_write_tokens"] += int(cache.get("write") or 0)
        if event.get("type") in {"tool_use", "tool"}:
            session_totals["tool_calls"] += 1
            name = str(part.get("tool") or part.get("name") or "unknown")
            session_totals["tool_counts"][name] += 1
            state = part.get("state", {})
            if event.get("type") == "tool_error" or (isinstance(state, dict) and state.get("status") == "error"):
                session_totals["tool_errors"] += 1
    return session_totals


def summarize_run(run_dir: Path) -> RunSummary | None:
    meta_path = run_dir / "meta.json"
    if not meta_path.is_file():
        return None
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ToolwrightError(f"{meta_path}: invalid JSON: {error}") from error
    session_totals = parse_session(run_dir / "session.jsonl")
    return RunSummary(
        run_id=str(meta.get("run_id", run_dir.name)),
        arm=str(meta.get("arm", "unknown")),
        task_id=str(meta.get("task_id", "unknown")),
        model=str(meta.get("model", "unknown")),
        agent=str(meta.get("agent", "unknown")),
        working_directory=str(meta.get("working_directory", ".")),
        cost=float(session_totals["cost"]),
        input_tokens=int(session_totals["input_tokens"]),
        output_tokens=int(session_totals["output_tokens"]),
        reasoning_tokens=int(session_totals["reasoning_tokens"]),
        cache_read_tokens=int(session_totals["cache_read_tokens"]),
        cache_write_tokens=int(session_totals["cache_write_tokens"]),
        steps=int(session_totals["steps"]),
        tool_calls=int(session_totals["tool_calls"]),
        tool_errors=int(session_totals["tool_errors"]),
        wall_time_seconds=int(meta.get("wall_time_seconds") or 0),
        verification_exit=meta.get("verification_exit"),
        tool_counts=dict(session_totals["tool_counts"]),
    )


def load_runs(results: Iterable[Path]) -> list[RunSummary]:
    runs: list[RunSummary] = []
    for path in results:
        if not path.is_dir():
            continue
        if (path / "meta.json").is_file():
            summary = summarize_run(path)
            if summary:
                runs.append(summary)
            continue
        for child in sorted(item for item in path.iterdir() if item.is_dir()):
            summary = summarize_run(child)
            if summary:
                runs.append(summary)
    return sorted(runs, key=lambda run: (run.task_id, run.arm, run.run_id))


def aggregate_totals(runs: list[RunSummary]) -> dict[str, Any]:
    return {
        "runs": len(runs),
        "cost": sum(run.cost for run in runs),
        "input_tokens": sum(run.input_tokens for run in runs),
        "output_tokens": sum(run.output_tokens for run in runs),
        "reasoning_tokens": sum(run.reasoning_tokens for run in runs),
        "cache_read_tokens": sum(run.cache_read_tokens for run in runs),
        "cache_write_tokens": sum(run.cache_write_tokens for run in runs),
        "steps": sum(run.steps for run in runs),
        "tool_calls": sum(run.tool_calls for run in runs),
        "tool_errors": sum(run.tool_errors for run in runs),
        "verified": sum(1 for run in runs if run.verification_exit == 0),
    }


def group_runs_by(runs: list[RunSummary], attribute: str) -> dict[str, dict[str, float]]:
    grouped: dict[str, dict[str, float]] = {}
    for run in runs:
        key = str(getattr(run, attribute))
        bucket = grouped.setdefault(key, {"runs": 0, "cost": 0.0, "tokens": 0, "tool_errors": 0})
        bucket["runs"] += 1
        bucket["cost"] += run.cost
        bucket["tokens"] += run.input_tokens + run.output_tokens
        bucket["tool_errors"] += run.tool_errors
    return grouped


def compare_arms(runs: list[RunSummary]) -> list[dict[str, Any]]:
    by_task: dict[str, dict[str, list[RunSummary]]] = {}
    for run in runs:
        by_task.setdefault(run.task_id, {}).setdefault(run.arm, []).append(run)
    comparisons: list[dict[str, Any]] = []
    for task, arms in sorted(by_task.items()):
        baseline_runs = arms.get("baseline", [])
        optimized_runs = arms.get("optimized", [])
        if not baseline_runs or not optimized_runs:
            continue
        baseline_cost = sum(run.cost for run in baseline_runs) / len(baseline_runs)
        optimized_cost = sum(run.cost for run in optimized_runs) / len(optimized_runs)
        baseline_tokens = sum(run.input_tokens + run.output_tokens for run in baseline_runs) / len(baseline_runs)
        optimized_tokens = sum(run.input_tokens + run.output_tokens for run in optimized_runs) / len(optimized_runs)
        comparisons.append(
            {
                "task": task,
                "baseline_runs": len(baseline_runs),
                "optimized_runs": len(optimized_runs),
                "baseline_cost": baseline_cost,
                "optimized_cost": optimized_cost,
                "baseline_tokens": baseline_tokens,
                "optimized_tokens": optimized_tokens,
                "cost_ratio": optimized_cost / baseline_cost if baseline_cost > 0 else None,
                "token_ratio": optimized_tokens / baseline_tokens if baseline_tokens > 0 else None,
                "baseline_pass_rate": sum(1 for run in baseline_runs if run.verification_exit == 0) / len(baseline_runs),
                "optimized_pass_rate": sum(1 for run in optimized_runs if run.verification_exit == 0) / len(optimized_runs),
            }
        )
    return comparisons


def render_markdown(runs: list[RunSummary]) -> str:
    if not runs:
        return "# Cost and Token Report\n\nNo completed result directories were found.\n"
    summary = aggregate_totals(runs)
    lines = [
        "# Cost and Token Report",
        "",
        "| Run | Arm | Task | Model | Agent | Cost | Input | Output | Steps | Tools | Errors | Wall | Verify |",
        "| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for run in runs:
        verify = "n/a" if run.verification_exit is None else str(run.verification_exit)
        lines.append(
            f"| {run.run_id} | {run.arm} | {run.task_id} | {run.model} | {run.agent} | "
            f"${run.cost:.6f} | {run.input_tokens} | {run.output_tokens} | {run.steps} | "
            f"{run.tool_calls} | {run.tool_errors} | {run.wall_time_seconds}s | {verify} |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- Runs: {summary['runs']}",
            f"- Verified: {summary['verified']}/{summary['runs']}",
            f"- Total cost: ${summary['cost']:.6f}",
            f"- Input tokens: {summary['input_tokens']}",
            f"- Output tokens: {summary['output_tokens']}",
            f"- Tool calls: {summary['tool_calls']} ({summary['tool_errors']} errors)",
            "",
        ]
    )
    for label, attribute in (("By agent", "agent"), ("By model", "model")):
        lines.extend([f"## {label}", "", "| Value | Runs | Cost | Tokens | Tool errors |", "| --- | ---: | ---: | ---: | ---: |"])
        for key, bucket in sorted(group_runs_by(runs, attribute).items()):
            lines.append(
                f"| {key} | {int(bucket['runs'])} | ${bucket['cost']:.6f} | {int(bucket['tokens'])} | {int(bucket['tool_errors'])} |"
            )
        lines.append("")
    tool_counts: Counter[str] = Counter()
    for run in runs:
        tool_counts.update(run.tool_counts)
    if tool_counts:
        lines.extend(["## By tool", "", "| Tool | Calls |", "| --- | ---: |"])
        for name, count in sorted(tool_counts.items()):
            lines.append(f"| {name} | {count} |")
        lines.append("")
    comparisons = compare_arms(runs)
    if comparisons:
        lines.extend(
            [
                "## Baseline vs optimized",
                "",
                "| Task | Baseline runs | Optimized runs | Baseline avg cost | Optimized avg cost | Cost ratio | Token ratio | Baseline pass | Optimized pass |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for item in comparisons:
            cost_ratio = "n/a" if item["cost_ratio"] is None else f"{item['cost_ratio']:.3f}"
            token_ratio = "n/a" if item["token_ratio"] is None else f"{item['token_ratio']:.3f}"
            lines.append(
                f"| {item['task']} | {item['baseline_runs']} | {item['optimized_runs']} | "
                f"${item['baseline_cost']:.6f} | ${item['optimized_cost']:.6f} | {cost_ratio} | "
                f"{token_ratio} | {item['baseline_pass_rate']:.0%} | {item['optimized_pass_rate']:.0%} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Notes",
            "",
            "Costs and tokens come from `session.jsonl` step-finish events. Correctness is the verification exit code; "
            "rework and human intervention must be recorded separately. A lower cost is not a better result unless "
            "correctness is equal or better.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_csv(runs: list[RunSummary]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(
        [
            "run_id",
            "arm",
            "task",
            "model",
            "agent",
            "cost",
            "input_tokens",
            "output_tokens",
            "reasoning_tokens",
            "cache_read_tokens",
            "cache_write_tokens",
            "steps",
            "tool_calls",
            "tool_errors",
            "wall_seconds",
            "verification_exit",
        ]
    )
    for run in runs:
        writer.writerow(
            [
                run.run_id,
                run.arm,
                run.task_id,
                run.model,
                run.agent,
                f"{run.cost:.6f}",
                run.input_tokens,
                run.output_tokens,
                run.reasoning_tokens,
                run.cache_read_tokens,
                run.cache_write_tokens,
                run.steps,
                run.tool_calls,
                run.tool_errors,
                run.wall_time_seconds,
                "" if run.verification_exit is None else run.verification_exit,
            ]
        )
    return buffer.getvalue()


def render_json(runs: list[RunSummary]) -> str:
    payload = {
        "runs": [
            {
                "run_id": run.run_id,
                "arm": run.arm,
                "task": run.task_id,
                "model": run.model,
                "agent": run.agent,
                "cost": run.cost,
                "input_tokens": run.input_tokens,
                "output_tokens": run.output_tokens,
                "reasoning_tokens": run.reasoning_tokens,
                "cache_read_tokens": run.cache_read_tokens,
                "cache_write_tokens": run.cache_write_tokens,
                "steps": run.steps,
                "tool_calls": run.tool_calls,
                "tool_errors": run.tool_errors,
                "tool_counts": run.tool_counts,
                "wall_time_seconds": run.wall_time_seconds,
                "verification_exit": run.verification_exit,
            }
            for run in runs
        ],
        "totals": aggregate_totals(runs),
        "by_agent": group_runs_by(runs, "agent"),
        "by_model": group_runs_by(runs, "model"),
        "comparison": compare_arms(runs),
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
