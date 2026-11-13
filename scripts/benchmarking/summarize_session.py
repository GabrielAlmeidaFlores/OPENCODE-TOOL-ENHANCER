#!/usr/bin/env python3
"""
Summarize one benchmark run from its session event log.

Public API: :func:`summarize`, :func:`main`.

Side effects: reads a session JSONL file and writes a JSON summary.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.lib.python_strings import (
    KEY_CACHE,
    KEY_CALLS,
    KEY_COST,
    KEY_INPUT,
    KEY_OUTPUT,
    KEY_PART,
    KEY_PROMPTS,
    KEY_READ,
    KEY_REASONING,
    KEY_STEPS,
    KEY_TOKENS,
    KEY_TOOLS,
    KEY_TYPE,
    KEY_WRITE,
    TEXT_MAIN,
    TEXT_TEXT_5 as TEXT_NEWLINE,
    TEXT_UTF_8,
)

EVENT_STEP_FINISH = "step_finish"
EVENT_TOOL_USE = "tool_use"
PROMPTS_PER_RUN = 1
TEXT_USAGE = "usage: summarize_session.py SESSION.jsonl OUTPUT.json"


def summarize(session_path: Path) -> dict[str, object]:
    """
    Aggregate token, cost, step, and tool totals from one session log.

    Parameters:
        session_path: JSONL file produced by ``opencode run --format json``.

    Returns:
        A dictionary with the same top-level shape used by benchmark reports.
    """
    tokens = {KEY_INPUT: 0, KEY_OUTPUT: 0, KEY_REASONING: 0, KEY_CACHE: {KEY_READ: 0, KEY_WRITE: 0}}
    steps = 0
    tool_calls = 0
    cost = 0.0
    for line in session_path.read_text(encoding=TEXT_UTF_8).splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        event_type = event.get(KEY_TYPE)
        if event_type == EVENT_STEP_FINISH:
            steps += 1
            part = event.get(KEY_PART, {})
            cost += float(part.get(KEY_COST) or 0)
            step_tokens = part.get(KEY_TOKENS, {})
            for key in (KEY_INPUT, KEY_OUTPUT, KEY_REASONING):
                tokens[key] += int(step_tokens.get(key, 0))
            cache = step_tokens.get(KEY_CACHE, {})
            tokens[KEY_CACHE][KEY_READ] += int(cache.get(KEY_READ, 0))
            tokens[KEY_CACHE][KEY_WRITE] += int(cache.get(KEY_WRITE, 0))
        elif event_type == EVENT_TOOL_USE:
            tool_calls += 1
    return {
        KEY_STEPS: steps,
        KEY_TOKENS: tokens,
        KEY_COST: cost,
        KEY_TOOLS: {KEY_CALLS: tool_calls},
        KEY_PROMPTS: PROMPTS_PER_RUN,
    }


def main() -> int:
    """
    Write a JSON summary for a session log.

    Usage: ``python3 scripts/benchmarking/summarize_session.py SESSION OUTPUT``.
    """
    if len(sys.argv) != 3:
        print(TEXT_USAGE, file=sys.stderr)
        return 2
    summary = summarize(Path(sys.argv[1]))
    Path(sys.argv[2]).write_text(json.dumps(summary, indent=2) + TEXT_NEWLINE, encoding=TEXT_UTF_8)
    return 0


if __name__ == TEXT_MAIN:
    sys.exit(main())
