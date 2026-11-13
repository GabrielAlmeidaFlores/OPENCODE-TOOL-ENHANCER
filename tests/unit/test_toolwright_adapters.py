"""
Unit tests for the adapter registry and planned-file hashing.
"""
from __future__ import annotations
from tests.unit.test_toolwright_adapters_strings import (
    KEY_AGENTS,
    KEY_CLAUDE,
    KEY_CODEX,
    KEY_COPILOT,
    KEY_COMMANDS,
    KEY_GENERATED,
    KEY_OPENCODE,
    KEY_RALPH,
    KEY_SKILLS,
    KEY_SOURCE,
    KEY_TARGET,
    KEY_UNKNOWN,
    TEXT_CLAUDE_AGENT,
    TEXT_MAIN,
    TEXT_OPENCODE_COPY,
    TEXT_SOURCE_MD,
    TEXT_TARGET_MD,
    TEXT_UTF_8,
)

import hashlib
import tempfile
import unittest
from pathlib import Path

from tests import support

from toolwright_cli import adapters
from toolwright_cli.locking import PlannedFile, planned_sha256
from toolwright_cli.paths import ToolWrightError


class RegistryTests(unittest.TestCase):

    def test_opencode_is_available(self) -> None:
        self.assertIn(KEY_OPENCODE, adapters.available_adapters())

    def test_unknown_adapter_is_rejected(self) -> None:
        with self.assertRaises(ToolWrightError):
            adapters.get_adapter(KEY_UNKNOWN)

    def test_opencode_supports_the_file_components(self) -> None:
        adapter = adapters.get_adapter(KEY_OPENCODE)
        self.assertTrue({KEY_OPENCODE, KEY_AGENTS, KEY_COMMANDS, KEY_SKILLS, KEY_RALPH}.issubset(adapter.supported_components))

    def test_opencode_plan_is_unchanged(self) -> None:
        planned = adapters.plan(
            KEY_OPENCODE,
            support.REPO_ROOT,
            support.REPO_ROOT / KEY_TARGET,
            [KEY_AGENTS],
        )
        self.assertEqual(len(planned), 12)
        self.assertTrue(all(item.adapter == KEY_OPENCODE for item in planned))
        self.assertTrue(all(item.generator == TEXT_OPENCODE_COPY for item in planned))


class PlatformAdapterTests(unittest.TestCase):

    def test_claude_plan_generates_agents_and_claude_md(self) -> None:
        planned = adapters.plan(KEY_CLAUDE, support.REPO_ROOT, support.REPO_ROOT / KEY_TARGET, [KEY_AGENTS])
        self.assertEqual(len(planned), 13)
        self.assertTrue(all(item.adapter == KEY_CLAUDE for item in planned))

    def test_copilot_plan_generates_instructions_and_agents_md(self) -> None:
        planned = adapters.plan(KEY_COPILOT, support.REPO_ROOT, support.REPO_ROOT / KEY_TARGET, [KEY_AGENTS])
        self.assertEqual(len(planned), 14)
        self.assertTrue(all(item.adapter == KEY_COPILOT for item in planned))

    def test_codex_plan_generates_toml_agents_and_agents_md(self) -> None:
        planned = adapters.plan(KEY_CODEX, support.REPO_ROOT, support.REPO_ROOT / KEY_TARGET, [KEY_AGENTS])
        self.assertEqual(len(planned), 13)
        self.assertTrue(all(item.adapter == KEY_CODEX for item in planned))


class PlannedHashTests(unittest.TestCase):

    def test_generated_content_is_hashed_without_a_source_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / TEXT_SOURCE_MD
            source.write_text(KEY_SOURCE, encoding=TEXT_UTF_8)
            item = PlannedFile(
                source=source,
                destination=Path(directory) / TEXT_TARGET_MD,
                component=KEY_AGENTS,
                adapter=KEY_CLAUDE,
                generator=TEXT_CLAUDE_AGENT,
                content=KEY_GENERATED,
            )
            self.assertEqual(planned_sha256(item), hashlib.sha256(b"generated").hexdigest())

    def test_copied_content_uses_the_source_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / TEXT_SOURCE_MD
            source.write_text(KEY_SOURCE, encoding=TEXT_UTF_8)
            item = PlannedFile(
                source=source,
                destination=Path(directory) / TEXT_TARGET_MD,
                component=KEY_AGENTS,
            )
            self.assertEqual(planned_sha256(item), hashlib.sha256(b"source").hexdigest())


if __name__ == TEXT_MAIN:
    unittest.main()
