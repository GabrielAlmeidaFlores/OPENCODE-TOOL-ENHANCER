"""
Unit tests for Markdown project memory.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tests import support

from ote_cli import memory
from ote_cli.paths import OteError


class MemoryTestCase(unittest.TestCase):
    """
    Base class providing a temporary repository root.
    """

    def setUp(self) -> None:
        """
        Create a temporary root with the memory layout.
        """
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def add(self, text: str, **options) -> memory.Entry:
        """
        Add a memory entry with test defaults.
        """
        defaults = {
            "entry_type": "decision",
            "title": None,
            "scope": "project",
            "source": "test",
            "confidence": 0.9,
            "links": [],
        }
        defaults.update(options)
        return memory.add(self.root, text, **defaults)


class AddTests(MemoryTestCase):
    """
    Tests for creating entries.
    """

    def test_add_creates_file_and_catalog(self) -> None:
        """
        A new entry is written and the catalog lists it.
        """
        entry = self.add("Use expand-and-contract migrations.", title="Migrations")
        self.assertTrue(entry.path.is_file())
        self.assertEqual(entry.entry_type, "decision")
        catalog = (self.root / ".ote/memory/catalog.md").read_text(encoding="utf-8")
        self.assertIn("Migrations", catalog)

    def test_duplicate_title_is_rejected(self) -> None:
        """
        The same title in the same scope is refused.
        """
        self.add("first", title="Same")
        with self.assertRaises(OteError):
            self.add("second", title="Same")

    def test_force_allows_duplicate_title(self) -> None:
        """
        --force permits a duplicate title.
        """
        self.add("first", title="Same")
        second = self.add("second", title="Same", force=True)
        self.assertTrue(second.path.is_file())

    def test_secret_is_rejected(self) -> None:
        """
        Credential-looking text is refused before writing.
        """
        with self.assertRaises(OteError) as raised:
            self.add("api_key=abcdefghijklmnop1234")
        self.assertIn("credential", str(raised.exception))
        self.assertFalse(list((self.root / ".ote/memory/project").glob("*.md")))

    def test_unknown_type_and_scope_are_rejected(self) -> None:
        """
        Invalid metadata is rejected.
        """
        with self.assertRaises(OteError):
            self.add("text", entry_type="nonsense")
        with self.assertRaises(OteError):
            self.add("text", scope="nonsense")

    def test_confidence_must_be_between_zero_and_one(self) -> None:
        """
        Confidence outside the range is rejected.
        """
        with self.assertRaises(OteError):
            self.add("text", confidence=1.5)

    def test_scopes_are_separate(self) -> None:
        """
        The same title may exist in two scopes.
        """
        self.add("project note", title="Same", scope="project")
        self.add("user note", title="Same", scope="user")
        self.assertEqual(len(memory.entries(self.root, "project")), 1)
        self.assertEqual(len(memory.entries(self.root, "user")), 1)


class SearchTests(MemoryTestCase):
    """
    Tests for lexical search and export.
    """

    def test_search_matches_title_body_and_type(self) -> None:
        """
        Search covers title, body, and entry type.
        """
        self.add("Use row-level security.", title="Postgres access", entry_type="constraint")
        self.assertEqual(len(memory.search(self.root, "row-level")), 1)
        self.assertEqual(len(memory.search(self.root, "Postgres")), 1)
        self.assertEqual(len(memory.search(self.root, "constraint")), 1)
        self.assertEqual(len(memory.search(self.root, "missing")), 0)
        self.assertEqual(memory.search(self.root, "   "), [])

    def test_search_filters_type(self) -> None:
        """
        Type filtering excludes other entry types.
        """
        self.add("a", title="Decision", entry_type="decision")
        self.add("b", title="Question", entry_type="question")
        results = memory.search(self.root, "e", entry_type="question")
        self.assertEqual([item.title for item in results], ["Question"])

    def test_export_json_and_markdown(self) -> None:
        """
        Both export formats contain the entry.
        """
        self.add("body", title="Export")
        payload = json.loads(memory.export(self.root, "json"))
        self.assertEqual(payload["entries"][0]["title"], "Export")
        markdown = memory.export(self.root, "markdown")
        self.assertIn("# Memory Export", markdown)
        self.assertIn("Export", markdown)


class PreambleTests(MemoryTestCase):
    """
    Tests for deterministic preamble rendering.
    """

    def test_scope_precedence(self) -> None:
        """
        Project entries appear before user and shared entries.
        """
        self.add("shared", title="Shared entry", scope="shared")
        self.add("user", title="User entry", scope="user")
        self.add("project", title="Project entry", scope="project")
        rendered = memory.preamble(self.root)
        self.assertLess(rendered.index("Project entry"), rendered.index("User entry"))
        self.assertLess(rendered.index("User entry"), rendered.index("Shared entry"))

    def test_budget_bounds_output(self) -> None:
        """
        A small budget excludes long entries.
        """
        self.add("x" * 400, title="Long entry")
        rendered = memory.preamble(self.root, budget_tokens=5)
        self.assertNotIn("Long entry", rendered)

    def test_invalid_budget_is_rejected(self) -> None:
        """
        A non-positive budget is rejected.
        """
        with self.assertRaises(OteError):
            memory.preamble(self.root, budget_tokens=0)


class PruneTests(MemoryTestCase):
    """
    Tests for expiry and pruning.
    """

    def _expire(self, entry: memory.Entry) -> None:
        """
        Rewrite an entry's expiry date to the past.
        """
        text = entry.path.read_text(encoding="utf-8")
        lines = [
            "expires: 2000-01-01" if line.startswith("expires:") else line
            for line in text.splitlines()
        ]
        entry.path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_prune_plan_keeps_files(self) -> None:
        """
        Without --apply, expired entries are reported but kept.
        """
        entry = self.add("old", title="Old")
        self._expire(entry)
        expired = memory.prune(self.root, apply=False)
        self.assertEqual(len(expired), 1)
        self.assertTrue(entry.path.is_file())

    def test_prune_apply_deletes_files(self) -> None:
        """
        With --apply, expired entries are removed and the catalog refreshed.
        """
        entry = self.add("old", title="Old")
        self._expire(entry)
        memory.prune(self.root, apply=True)
        self.assertFalse(entry.path.exists())
        catalog = (self.root / ".ote/memory/catalog.md").read_text(encoding="utf-8")
        self.assertNotIn("Old", catalog)


if __name__ == "__main__":
    unittest.main()
