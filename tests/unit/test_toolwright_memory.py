"""
Unit tests for Markdown project memory.
"""
from __future__ import annotations
from tests.unit.test_toolwright_memory_strings import (
    KEY_A,
    KEY_B,
    KEY_BODY,
    KEY_CONFIDENCE,
    KEY_CONSTRAINT,
    KEY_CREDENTIAL,
    KEY_DECISION,
    KEY_E,
    KEY_ENTRIES,
    KEY_ENTRY_TYPE,
    KEY_FIRST,
    KEY_JSON,
    KEY_LINKS,
    KEY_MARKDOWN,
    KEY_MISSING,
    KEY_NONSENSE,
    KEY_OLD,
    KEY_PROJECT,
    KEY_QUESTION,
    KEY_SCOPE,
    KEY_SECOND,
    KEY_SHARED,
    KEY_SOURCE,
    KEY_TEST,
    KEY_TEXT,
    KEY_TITLE,
    KEY_USER,
    KEY_X,
    TEXT_API_KEY_ABCDEFGHIJKLMNOP1234,
    TEXT_BAD_TYPE_FAILURE,
    TEXT_DECISION,
    TEXT_EXPIRES,
    TEXT_EXPIRES_2000_01_01,
    TEXT_EXPORT,
    TEXT_LONG_ENTRY,
    TEXT_MAIN,
    TEXT_MD,
    TEXT_MEMORY_EXPORT,
    TEXT_MIGRATIONS,
    TEXT_OLD,
    TEXT_POSTGRES,
    TEXT_POSTGRES_ACCESS,
    TEXT_PROJECT_ENTRY,
    TEXT_PROJECT_NOTE,
    TEXT_QUESTION,
    TEXT_ROW_LEVEL,
    TEXT_SAME,
    TEXT_SHARED_ENTRY,
    TEXT_TEXT,
    TEXT_TEXT_2,
    TEXT_TOOLWRIGHT_MEMORY_CATALOG_MD,
    TEXT_TOOLWRIGHT_MEMORY_PROJECT,
    TEXT_USER_ENTRY,
    TEXT_USER_NOTE,
    TEXT_USE_EXPAND_AND_CONTRACT_MIGRATIONS,
    TEXT_USE_ROW_LEVEL_SECURITY,
    TEXT_UTF_8,
)

import json
import tempfile
import unittest
from pathlib import Path

from tests import support

from toolwright_cli import memory
from toolwright_cli.paths import ToolWrightError


class MemoryTestCase(unittest.TestCase):

    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def add(self, text: str, **options) -> memory.Entry:
        defaults = {
            KEY_ENTRY_TYPE: KEY_DECISION,
            KEY_TITLE: None,
            KEY_SCOPE: KEY_PROJECT,
            KEY_SOURCE: KEY_TEST,
            KEY_CONFIDENCE: 0.9,
            KEY_LINKS: [],
        }
        defaults.update(options)
        return memory.add_memory_entry(self.root, text, **defaults)


class AddTests(MemoryTestCase):

    def test_add_creates_file_and_catalog(self) -> None:
        entry = self.add(TEXT_USE_EXPAND_AND_CONTRACT_MIGRATIONS, title=TEXT_MIGRATIONS)
        self.assertTrue(entry.path.is_file())
        self.assertEqual(entry.entry_type, KEY_DECISION)
        catalog = (self.root / TEXT_TOOLWRIGHT_MEMORY_CATALOG_MD).read_text(encoding=TEXT_UTF_8)
        self.assertIn(TEXT_MIGRATIONS, catalog)

    def test_duplicate_title_is_rejected(self) -> None:
        self.add(KEY_FIRST, title=TEXT_SAME)
        with self.assertRaises(ToolWrightError):
            self.add(KEY_SECOND, title=TEXT_SAME)

    def test_force_allows_duplicate_title(self) -> None:
        self.add(KEY_FIRST, title=TEXT_SAME)
        second = self.add(KEY_SECOND, title=TEXT_SAME, force=True)
        self.assertTrue(second.path.is_file())

    def test_secret_is_rejected(self) -> None:
        with self.assertRaises(ToolWrightError) as raised:
            self.add(TEXT_API_KEY_ABCDEFGHIJKLMNOP1234)
        self.assertIn(KEY_CREDENTIAL, str(raised.exception))
        self.assertFalse(list((self.root / TEXT_TOOLWRIGHT_MEMORY_PROJECT).glob(TEXT_MD)))

    def test_multiline_title_is_rejected(self) -> None:
        with self.assertRaises(ToolWrightError):
            self.add(KEY_BODY, title=TEXT_BAD_TYPE_FAILURE)
        self.assertFalse(list((self.root / TEXT_TOOLWRIGHT_MEMORY_PROJECT).glob(TEXT_MD)))

    def test_unknown_type_and_scope_are_rejected(self) -> None:
        with self.assertRaises(ToolWrightError):
            self.add(KEY_TEXT, entry_type=KEY_NONSENSE)
        with self.assertRaises(ToolWrightError):
            self.add(KEY_TEXT, scope=KEY_NONSENSE)

    def test_confidence_must_be_between_zero_and_one(self) -> None:
        with self.assertRaises(ToolWrightError):
            self.add(KEY_TEXT, confidence=1.5)

    def test_scopes_are_separate(self) -> None:
        self.add(TEXT_PROJECT_NOTE, title=TEXT_SAME, scope=KEY_PROJECT)
        self.add(TEXT_USER_NOTE, title=TEXT_SAME, scope=KEY_USER)
        self.assertEqual(len(memory.load_memory_entries(self.root, KEY_PROJECT)), 1)
        self.assertEqual(len(memory.load_memory_entries(self.root, KEY_USER)), 1)


class SearchTests(MemoryTestCase):

    def test_search_matches_title_body_and_type(self) -> None:
        self.add(TEXT_USE_ROW_LEVEL_SECURITY, title=TEXT_POSTGRES_ACCESS, entry_type=KEY_CONSTRAINT)
        self.assertEqual(len(memory.search_memory_entries(self.root, TEXT_ROW_LEVEL)), 1)
        self.assertEqual(len(memory.search_memory_entries(self.root, TEXT_POSTGRES)), 1)
        self.assertEqual(len(memory.search_memory_entries(self.root, KEY_CONSTRAINT)), 1)
        self.assertEqual(len(memory.search_memory_entries(self.root, KEY_MISSING)), 0)
        self.assertEqual(memory.search_memory_entries(self.root, TEXT_TEXT), [])

    def test_search_filters_type(self) -> None:
        self.add(KEY_A, title=TEXT_DECISION, entry_type=KEY_DECISION)
        self.add(KEY_B, title=TEXT_QUESTION, entry_type=KEY_QUESTION)
        results = memory.search_memory_entries(self.root, KEY_E, entry_type=KEY_QUESTION)
        self.assertEqual([item.title for item in results], [TEXT_QUESTION])

    def test_export_json_and_markdown(self) -> None:
        self.add(KEY_BODY, title=TEXT_EXPORT)
        payload = json.loads(memory.export_memory_entries(self.root, KEY_JSON))
        self.assertEqual(payload[KEY_ENTRIES][0][KEY_TITLE], TEXT_EXPORT)
        markdown = memory.export_memory_entries(self.root, KEY_MARKDOWN)
        self.assertIn(TEXT_MEMORY_EXPORT, markdown)
        self.assertIn(TEXT_EXPORT, markdown)


class PreambleTests(MemoryTestCase):

    def test_scope_precedence(self) -> None:
        self.add(KEY_SHARED, title=TEXT_SHARED_ENTRY, scope=KEY_SHARED)
        self.add(KEY_USER, title=TEXT_USER_ENTRY, scope=KEY_USER)
        self.add(KEY_PROJECT, title=TEXT_PROJECT_ENTRY, scope=KEY_PROJECT)
        rendered = memory.render_memory_preamble(self.root)
        self.assertLess(rendered.index(TEXT_PROJECT_ENTRY), rendered.index(TEXT_USER_ENTRY))
        self.assertLess(rendered.index(TEXT_USER_ENTRY), rendered.index(TEXT_SHARED_ENTRY))

    def test_budget_bounds_output(self) -> None:
        self.add(KEY_X * 400, title=TEXT_LONG_ENTRY)
        rendered = memory.render_memory_preamble(self.root, budget_tokens=5)
        self.assertNotIn(TEXT_LONG_ENTRY, rendered)

    def test_invalid_budget_is_rejected(self) -> None:
        with self.assertRaises(ToolWrightError):
            memory.render_memory_preamble(self.root, budget_tokens=0)


class PruneTests(MemoryTestCase):

    def _expire(self, entry: memory.Entry) -> None:
        text = entry.path.read_text(encoding=TEXT_UTF_8)
        lines = [
            TEXT_EXPIRES_2000_01_01 if line.startswith(TEXT_EXPIRES) else line
            for line in text.splitlines()
        ]
        entry.path.write_text(TEXT_TEXT_2.join(lines) + TEXT_TEXT_2, encoding=TEXT_UTF_8)

    def test_prune_plan_keeps_files(self) -> None:
        entry = self.add(KEY_OLD, title=TEXT_OLD)
        self._expire(entry)
        expired = memory.prune_expired_entries(self.root, apply=False)
        self.assertEqual(len(expired), 1)
        self.assertTrue(entry.path.is_file())

    def test_prune_apply_deletes_files(self) -> None:
        entry = self.add(KEY_OLD, title=TEXT_OLD)
        self._expire(entry)
        memory.prune_expired_entries(self.root, apply=True)
        self.assertFalse(entry.path.exists())
        catalog = (self.root / TEXT_TOOLWRIGHT_MEMORY_CATALOG_MD).read_text(encoding=TEXT_UTF_8)
        self.assertNotIn(TEXT_OLD, catalog)


if __name__ == TEXT_MAIN:
    unittest.main()
