"""
Unit tests for benchmark session summarization.

Public API: none. The module is a unittest test case.

Side effects: writes only inside a temporary directory.
"""
from __future__ import annotations
from tests.constants import (
    TEXT_MAIN,
    TEXT_RUN_STATS_JSON,
    TEXT_SCRIPTS_BENCHMARKING_SUMMARIZE_SESSION_PY,
    TEXT_SESSION_JSONL,
    TEXT_UTF_8,
)

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests import support

from scripts.benchmarking.summarize_session import (
    EVENT_STEP_FINISH,
    EVENT_TOOL_USE,
    KEY_CACHE,
    KEY_CALLS,
    KEY_COST,
    KEY_INPUT,
    KEY_OUTPUT,
    KEY_PART,
    KEY_READ,
    KEY_REASONING,
    KEY_STEPS,
    KEY_TOKENS,
    KEY_TOOLS,
    KEY_TYPE,
    KEY_WRITE,
    summarize,
)


class SessionSummaryTests(unittest.TestCase):

    def test_summarizes_cost_tokens_steps_and_tools(self) -> None:
        events = [
            {
                KEY_TYPE: EVENT_STEP_FINISH,
                KEY_PART: {
                    KEY_COST: 0.25,
                    KEY_TOKENS: {
                        KEY_INPUT: 100,
                        KEY_OUTPUT: 20,
                        KEY_REASONING: 5,
                        KEY_CACHE: {KEY_READ: 40, KEY_WRITE: 0},
                    },
                },
            },
            {KEY_TYPE: EVENT_TOOL_USE, KEY_PART: {}},
            {
                KEY_TYPE: EVENT_STEP_FINISH,
                KEY_PART: {
                    KEY_COST: 0.5,
                    KEY_TOKENS: {
                        KEY_INPUT: 200,
                        KEY_OUTPUT: 30,
                        KEY_REASONING: 7,
                        KEY_CACHE: {KEY_READ: 60, KEY_WRITE: 0},
                    },
                },
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            session = Path(directory) / TEXT_SESSION_JSONL
            session.write_text(
                "\n".join(json.dumps(event) for event in events),
                encoding=TEXT_UTF_8,
            )
            summary = summarize(session)
        self.assertEqual(summary[KEY_STEPS], 2)
        self.assertEqual(summary[KEY_TOOLS][KEY_CALLS], 1)
        self.assertAlmostEqual(summary[KEY_COST], 0.75)
        self.assertEqual(summary[KEY_TOKENS][KEY_INPUT], 300)
        self.assertEqual(summary[KEY_TOKENS][KEY_OUTPUT], 50)
        self.assertEqual(summary[KEY_TOKENS][KEY_REASONING], 12)
        self.assertEqual(summary[KEY_TOKENS][KEY_CACHE][KEY_READ], 100)

    def test_script_entrypoint_writes_summary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            session = Path(directory) / TEXT_SESSION_JSONL
            output = Path(directory) / TEXT_RUN_STATS_JSON
            session.write_text(
                json.dumps(
                    {
                        KEY_TYPE: EVENT_STEP_FINISH,
                        KEY_PART: {
                            KEY_COST: 0.5,
                            KEY_TOKENS: {
                                KEY_INPUT: 10,
                                KEY_OUTPUT: 5,
                                KEY_REASONING: 1,
                                KEY_CACHE: {KEY_READ: 0, KEY_WRITE: 0},
                            },
                        },
                    }
                ),
                encoding=TEXT_UTF_8,
            )
            result = subprocess.run(
                [
                    sys.executable,
                    TEXT_SCRIPTS_BENCHMARKING_SUMMARIZE_SESSION_PY,
                    str(session),
                    str(output),
                ],
                cwd=support.REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            summary = json.loads(output.read_text(encoding=TEXT_UTF_8))
        self.assertEqual(summary[KEY_STEPS], 1)
        self.assertAlmostEqual(summary[KEY_COST], 0.5)


if __name__ == TEXT_MAIN:
    unittest.main()
