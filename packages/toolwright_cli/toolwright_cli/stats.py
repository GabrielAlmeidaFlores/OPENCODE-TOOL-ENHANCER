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
from .stats_strings import (
    DEFAULT_COMMIT,
    EMPTY_STRING,
    ENCODING_UTF8,
    KEY_AGENT,
    KEY_ARM,
    KEY_BASELINE,
    KEY_BASELINE_COST,
    KEY_BASELINE_PASS_RATE,
    KEY_BASELINE_RUNS,
    KEY_BASELINE_TOKENS,
    KEY_BY_AGENT,
    KEY_BY_MODEL,
    KEY_CACHE,
    KEY_CACHE_READ_TOKENS,
    KEY_CACHE_WRITE_TOKENS,
    KEY_COMPARISON,
    KEY_COST,
    KEY_COST_RATIO,
    KEY_ERROR,
    KEY_IGNORE,
    KEY_INPUT,
    KEY_INPUT_TOKENS,
    KEY_MODEL,
    KEY_NAME,
    KEY_OPTIMIZED,
    KEY_OPTIMIZED_COST,
    KEY_OPTIMIZED_PASS_RATE,
    KEY_OPTIMIZED_RUNS,
    KEY_OPTIMIZED_TOKENS,
    KEY_OUTPUT,
    KEY_OUTPUT_TOKENS,
    KEY_PART,
    KEY_READ,
    KEY_REASONING,
    KEY_REASONING_TOKENS,
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
    KEY_TOOL_ERROR,
    KEY_TOOL_ERRORS,
    KEY_TOOL_USE,
    KEY_TOTALS,
    KEY_TYPE,
    KEY_VERIFICATION_EXIT,
    KEY_VERIFIED,
    KEY_WALL_SECONDS,
    KEY_WALL_TIME_SECONDS,
    KEY_WORKING_DIRECTORY,
    KEY_WRITE,
    NEWLINE,
    TEXT_3F,
    TEXT_6F,
    TEXT_6F_2,
    TEXT_6F_6F_0_0,
    TEXT_6F_S,
    TEXT_BASELINE_VS_OPTIMIZED,
    TEXT_BY_AGENT,
    TEXT_BY_MODEL,
    TEXT_BY_TOOL,
    TEXT_CORRECTNESS_IS_EQUAL_OR_BETTER,
    TEXT_COSTS_AND_TOKENS_COME_FROM_SESSION_JSONL_STEP_FINISH_EVENTS_,
    TEXT_COST_AND_TOKEN_REPORT,
    TEXT_COST_AND_TOKEN_REPORT_NO_COMPLETED_RESULT_DIRECTORIES_WERE_F,
    TEXT_INPUT_TOKENS,
    TEXT_INVALID_JSON,
    TEXT_META_JSON,
    TEXT_NOTES,
    TEXT_N_A,
    TEXT_OUTPUT_TOKENS,
    TEXT_REWORK_AND_HUMAN_INTERVENTION_MUST_BE_RECORDED_SEPARATELY_A_,
    TEXT_RUNS,
    TEXT_RUN_ARM_TASK_MODEL_AGENT_COST_INPUT_OUTPUT_STEPS_TOOLS_ERROR,
    TEXT_SESSION_JSONL,
    TEXT_SUMMARY,
    TEXT_TASK_BASELINE_RUNS_OPTIMIZED_RUNS_BASELINE_AVG_COST_OPTIMIZE,
    TEXT_TEXT,
    TEXT_TEXT_2,
    TEXT_TEXT_3,
    TEXT_TEXT_4,
    TEXT_TEXT_5,
    TEXT_TEXT_6,
    TEXT_TEXT_7,
    TEXT_TOOL_CALLS,
    TEXT_TOOL_CALLS_ERRORS,
    TEXT_TOTAL_COST_6F,
    TEXT_VALUE_RUNS_COST_TOKENS_TOOL_ERRORS,
    TEXT_VERIFIED,
)

import csv
import io
import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from .paths import ToolWrightError


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
        KEY_COST: 0.0,
        KEY_INPUT_TOKENS: 0,
        KEY_OUTPUT_TOKENS: 0,
        KEY_REASONING_TOKENS: 0,
        KEY_CACHE_READ_TOKENS: 0,
        KEY_CACHE_WRITE_TOKENS: 0,
        KEY_STEPS: 0,
        KEY_TOOL_CALLS: 0,
        KEY_TOOL_ERRORS: 0,
        KEY_TOOL_COUNTS: Counter(),
    }


def parse_session(session_path: Path) -> dict[str, Any]:
    session_totals = empty_session_totals()
    if not session_path.is_file():
        return session_totals
    for line in session_path.read_text(encoding=ENCODING_UTF8, errors=KEY_IGNORE).splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        part = event.get(KEY_PART, {})
        if event.get(KEY_TYPE) == KEY_STEP_FINISH:
            session_totals[KEY_STEPS] += 1
            session_totals[KEY_COST] += float(part.get(KEY_COST) or 0.0)
            tokens = part.get(KEY_TOKENS, {})
            session_totals[KEY_INPUT_TOKENS] += int(tokens.get(KEY_INPUT) or 0)
            session_totals[KEY_OUTPUT_TOKENS] += int(tokens.get(KEY_OUTPUT) or 0)
            session_totals[KEY_REASONING_TOKENS] += int(tokens.get(KEY_REASONING) or 0)
            cache = tokens.get(KEY_CACHE, {})
            session_totals[KEY_CACHE_READ_TOKENS] += int(cache.get(KEY_READ) or 0)
            session_totals[KEY_CACHE_WRITE_TOKENS] += int(cache.get(KEY_WRITE) or 0)
        if event.get(KEY_TYPE) in {KEY_TOOL_USE, KEY_TOOL}:
            session_totals[KEY_TOOL_CALLS] += 1
            name = str(part.get(KEY_TOOL) or part.get(KEY_NAME) or DEFAULT_COMMIT)
            session_totals[KEY_TOOL_COUNTS][name] += 1
            state = part.get(KEY_STATE, {})
            if event.get(KEY_TYPE) == KEY_TOOL_ERROR or (isinstance(state, dict) and state.get(KEY_STATUS) == KEY_ERROR):
                session_totals[KEY_TOOL_ERRORS] += 1
    return session_totals


def summarize_run(run_dir: Path) -> RunSummary | None:
    meta_path = run_dir / TEXT_META_JSON
    if not meta_path.is_file():
        return None
    try:
        meta = json.loads(meta_path.read_text(encoding=ENCODING_UTF8))
    except json.JSONDecodeError as error:
        raise ToolWrightError(TEXT_INVALID_JSON.format(meta_path, error)) from error
    session_totals = parse_session(run_dir / TEXT_SESSION_JSONL)
    return RunSummary(
        run_id=str(meta.get(KEY_RUN_ID, run_dir.name)),
        arm=str(meta.get(KEY_ARM, DEFAULT_COMMIT)),
        task_id=str(meta.get(KEY_TASK_ID, DEFAULT_COMMIT)),
        model=str(meta.get(KEY_MODEL, DEFAULT_COMMIT)),
        agent=str(meta.get(KEY_AGENT, DEFAULT_COMMIT)),
        working_directory=str(meta.get(KEY_WORKING_DIRECTORY, TEXT_TEXT_3)),
        cost=float(session_totals[KEY_COST]),
        input_tokens=int(session_totals[KEY_INPUT_TOKENS]),
        output_tokens=int(session_totals[KEY_OUTPUT_TOKENS]),
        reasoning_tokens=int(session_totals[KEY_REASONING_TOKENS]),
        cache_read_tokens=int(session_totals[KEY_CACHE_READ_TOKENS]),
        cache_write_tokens=int(session_totals[KEY_CACHE_WRITE_TOKENS]),
        steps=int(session_totals[KEY_STEPS]),
        tool_calls=int(session_totals[KEY_TOOL_CALLS]),
        tool_errors=int(session_totals[KEY_TOOL_ERRORS]),
        wall_time_seconds=int(meta.get(KEY_WALL_TIME_SECONDS) or 0),
        verification_exit=meta.get(KEY_VERIFICATION_EXIT),
        tool_counts=dict(session_totals[KEY_TOOL_COUNTS]),
    )


def load_runs(results: Iterable[Path]) -> list[RunSummary]:
    runs: list[RunSummary] = []
    for path in results:
        if not path.is_dir():
            continue
        if (path / TEXT_META_JSON).is_file():
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
        KEY_RUNS: len(runs),
        KEY_COST: sum(run.cost for run in runs),
        KEY_INPUT_TOKENS: sum(run.input_tokens for run in runs),
        KEY_OUTPUT_TOKENS: sum(run.output_tokens for run in runs),
        KEY_REASONING_TOKENS: sum(run.reasoning_tokens for run in runs),
        KEY_CACHE_READ_TOKENS: sum(run.cache_read_tokens for run in runs),
        KEY_CACHE_WRITE_TOKENS: sum(run.cache_write_tokens for run in runs),
        KEY_STEPS: sum(run.steps for run in runs),
        KEY_TOOL_CALLS: sum(run.tool_calls for run in runs),
        KEY_TOOL_ERRORS: sum(run.tool_errors for run in runs),
        KEY_VERIFIED: sum(1 for run in runs if run.verification_exit == 0),
    }


def group_runs_by(runs: list[RunSummary], attribute: str) -> dict[str, dict[str, float]]:
    grouped: dict[str, dict[str, float]] = {}
    for run in runs:
        key = str(getattr(run, attribute))
        bucket = grouped.setdefault(key, {KEY_RUNS: 0, KEY_COST: 0.0, KEY_TOKENS: 0, KEY_TOOL_ERRORS: 0})
        bucket[KEY_RUNS] += 1
        bucket[KEY_COST] += run.cost
        bucket[KEY_TOKENS] += run.input_tokens + run.output_tokens
        bucket[KEY_TOOL_ERRORS] += run.tool_errors
    return grouped


def compare_arms(runs: list[RunSummary]) -> list[dict[str, Any]]:
    by_task: dict[str, dict[str, list[RunSummary]]] = {}
    for run in runs:
        by_task.setdefault(run.task_id, {}).setdefault(run.arm, []).append(run)
    comparisons: list[dict[str, Any]] = []
    for task, arms in sorted(by_task.items()):
        baseline_runs = arms.get(KEY_BASELINE, [])
        optimized_runs = arms.get(KEY_OPTIMIZED, [])
        if not baseline_runs or not optimized_runs:
            continue
        baseline_cost = sum(run.cost for run in baseline_runs) / len(baseline_runs)
        optimized_cost = sum(run.cost for run in optimized_runs) / len(optimized_runs)
        baseline_tokens = sum(run.input_tokens + run.output_tokens for run in baseline_runs) / len(baseline_runs)
        optimized_tokens = sum(run.input_tokens + run.output_tokens for run in optimized_runs) / len(optimized_runs)
        comparisons.append(
            {
                KEY_TASK: task,
                KEY_BASELINE_RUNS: len(baseline_runs),
                KEY_OPTIMIZED_RUNS: len(optimized_runs),
                KEY_BASELINE_COST: baseline_cost,
                KEY_OPTIMIZED_COST: optimized_cost,
                KEY_BASELINE_TOKENS: baseline_tokens,
                KEY_OPTIMIZED_TOKENS: optimized_tokens,
                KEY_COST_RATIO: optimized_cost / baseline_cost if baseline_cost > 0 else None,
                KEY_TOKEN_RATIO: optimized_tokens / baseline_tokens if baseline_tokens > 0 else None,
                KEY_BASELINE_PASS_RATE: sum(1 for run in baseline_runs if run.verification_exit == 0) / len(baseline_runs),
                KEY_OPTIMIZED_PASS_RATE: sum(1 for run in optimized_runs if run.verification_exit == 0) / len(optimized_runs),
            }
        )
    return comparisons


def render_markdown(runs: list[RunSummary]) -> str:
    if not runs:
        return TEXT_COST_AND_TOKEN_REPORT_NO_COMPLETED_RESULT_DIRECTORIES_WERE_F
    summary = aggregate_totals(runs)
    lines = [
        TEXT_COST_AND_TOKEN_REPORT,
        EMPTY_STRING,
        TEXT_RUN_ARM_TASK_MODEL_AGENT_COST_INPUT_OUTPUT_STEPS_TOOLS_ERROR,
        TEXT_TEXT_4,
    ]
    for run in runs:
        verify = TEXT_N_A if run.verification_exit is None else str(run.verification_exit)
        lines.append(
            TEXT_6F_S.format(run.run_id, run.arm, run.task_id, run.model, run.agent, run.cost, run.input_tokens, run.output_tokens, run.steps, run.tool_calls, run.tool_errors, run.wall_time_seconds, verify)
        )
    lines.extend(
        [
            EMPTY_STRING,
            TEXT_SUMMARY,
            EMPTY_STRING,
            TEXT_RUNS.format(summary[KEY_RUNS]),
            TEXT_VERIFIED.format(summary[KEY_VERIFIED], summary[KEY_RUNS]),
            TEXT_TOTAL_COST_6F.format(summary[KEY_COST]),
            TEXT_INPUT_TOKENS.format(summary[KEY_INPUT_TOKENS]),
            TEXT_OUTPUT_TOKENS.format(summary[KEY_OUTPUT_TOKENS]),
            TEXT_TOOL_CALLS_ERRORS.format(summary[KEY_TOOL_CALLS], summary[KEY_TOOL_ERRORS]),
            EMPTY_STRING,
        ]
    )
    for label, attribute in ((TEXT_BY_AGENT, KEY_AGENT), (TEXT_BY_MODEL, KEY_MODEL)):
        lines.extend([TEXT_TEXT.format(label), EMPTY_STRING, TEXT_VALUE_RUNS_COST_TOKENS_TOOL_ERRORS, TEXT_TEXT_5])
        for key, bucket in sorted(group_runs_by(runs, attribute).items()):
            lines.append(
                TEXT_6F.format(key, int(bucket[KEY_RUNS]), bucket[KEY_COST], int(bucket[KEY_TOKENS]), int(bucket[KEY_TOOL_ERRORS]))
            )
        lines.append(EMPTY_STRING)
    tool_counts: Counter[str] = Counter()
    for run in runs:
        tool_counts.update(run.tool_counts)
    if tool_counts:
        lines.extend([TEXT_BY_TOOL, EMPTY_STRING, TEXT_TOOL_CALLS, TEXT_TEXT_6])
        for name, count in sorted(tool_counts.items()):
            lines.append(TEXT_TEXT_2.format(name, count))
        lines.append(EMPTY_STRING)
    comparisons = compare_arms(runs)
    if comparisons:
        lines.extend(
            [
                TEXT_BASELINE_VS_OPTIMIZED,
                EMPTY_STRING,
                TEXT_TASK_BASELINE_RUNS_OPTIMIZED_RUNS_BASELINE_AVG_COST_OPTIMIZE,
                TEXT_TEXT_7,
            ]
        )
        for item in comparisons:
            cost_ratio = TEXT_N_A if item[KEY_COST_RATIO] is None else TEXT_3F.format(item[KEY_COST_RATIO])
            token_ratio = TEXT_N_A if item[KEY_TOKEN_RATIO] is None else TEXT_3F.format(item[KEY_TOKEN_RATIO])
            lines.append(
                TEXT_6F_6F_0_0.format(item[KEY_TASK], item[KEY_BASELINE_RUNS], item[KEY_OPTIMIZED_RUNS], item[KEY_BASELINE_COST], item[KEY_OPTIMIZED_COST], cost_ratio, token_ratio, item[KEY_BASELINE_PASS_RATE], item[KEY_OPTIMIZED_PASS_RATE])
            )
        lines.append(EMPTY_STRING)
    lines.extend(
        [
            TEXT_NOTES,
            EMPTY_STRING,
            TEXT_COSTS_AND_TOKENS_COME_FROM_SESSION_JSONL_STEP_FINISH_EVENTS_,
            TEXT_REWORK_AND_HUMAN_INTERVENTION_MUST_BE_RECORDED_SEPARATELY_A_,
            TEXT_CORRECTNESS_IS_EQUAL_OR_BETTER,
        ]
    )
    return NEWLINE.join(lines) + NEWLINE


def render_csv(runs: list[RunSummary]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator=NEWLINE)
    writer.writerow(
        [
            KEY_RUN_ID,
            KEY_ARM,
            KEY_TASK,
            KEY_MODEL,
            KEY_AGENT,
            KEY_COST,
            KEY_INPUT_TOKENS,
            KEY_OUTPUT_TOKENS,
            KEY_REASONING_TOKENS,
            KEY_CACHE_READ_TOKENS,
            KEY_CACHE_WRITE_TOKENS,
            KEY_STEPS,
            KEY_TOOL_CALLS,
            KEY_TOOL_ERRORS,
            KEY_WALL_SECONDS,
            KEY_VERIFICATION_EXIT,
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
                TEXT_6F_2.format(run.cost),
                run.input_tokens,
                run.output_tokens,
                run.reasoning_tokens,
                run.cache_read_tokens,
                run.cache_write_tokens,
                run.steps,
                run.tool_calls,
                run.tool_errors,
                run.wall_time_seconds,
                EMPTY_STRING if run.verification_exit is None else run.verification_exit,
            ]
        )
    return buffer.getvalue()


def render_json(runs: list[RunSummary]) -> str:
    payload = {
        KEY_RUNS: [
            {
                KEY_RUN_ID: run.run_id,
                KEY_ARM: run.arm,
                KEY_TASK: run.task_id,
                KEY_MODEL: run.model,
                KEY_AGENT: run.agent,
                KEY_COST: run.cost,
                KEY_INPUT_TOKENS: run.input_tokens,
                KEY_OUTPUT_TOKENS: run.output_tokens,
                KEY_REASONING_TOKENS: run.reasoning_tokens,
                KEY_CACHE_READ_TOKENS: run.cache_read_tokens,
                KEY_CACHE_WRITE_TOKENS: run.cache_write_tokens,
                KEY_STEPS: run.steps,
                KEY_TOOL_CALLS: run.tool_calls,
                KEY_TOOL_ERRORS: run.tool_errors,
                KEY_TOOL_COUNTS: run.tool_counts,
                KEY_WALL_TIME_SECONDS: run.wall_time_seconds,
                KEY_VERIFICATION_EXIT: run.verification_exit,
            }
            for run in runs
        ],
        KEY_TOTALS: aggregate_totals(runs),
        KEY_BY_AGENT: group_runs_by(runs, KEY_AGENT),
        KEY_BY_MODEL: group_runs_by(runs, KEY_MODEL),
        KEY_COMPARISON: compare_arms(runs),
    }
    return json.dumps(payload, indent=2, sort_keys=True) + NEWLINE
