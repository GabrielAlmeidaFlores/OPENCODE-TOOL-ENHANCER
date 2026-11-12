"""
Unit tests for the verified artifact catalog.
"""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tests import support

from ote_cli import catalog
from ote_cli.paths import OteError


class CatalogRepositoryTests(unittest.TestCase):
    """
    Tests against the committed generated catalog.
    """

    def test_catalog_loads(self) -> None:
        """
        The committed catalog is valid JSON with the expected sections.
        """
        document = catalog.load_catalog(support.REPO_ROOT)
        self.assertEqual(document["schema_version"], 1)
        self.assertIn("artifacts", document)
        self.assertGreater(len(document["artifacts"]), 0)

    def test_verify_passes(self) -> None:
        """
        Every committed entry satisfies the schema and exists on disk.
        """
        document = catalog.load_catalog(support.REPO_ROOT)
        results = catalog.verify(support.REPO_ROOT, document)
        failures = [result for result in results if result["status"] == "fail"]
        self.assertEqual(failures, [])

    def test_search_matches_metadata(self) -> None:
        """
        Search matches ids, authors, and licenses case-insensitively.
        """
        document = catalog.load_catalog(support.REPO_ROOT)
        self.assertTrue(catalog.search(document, "security"))
        self.assertTrue(catalog.search(document, "MIT"))
        self.assertEqual(catalog.search(document, "no-such-artifact"), [])
        self.assertEqual(catalog.search(document, "   "), [])

    def test_missing_catalog_is_an_error(self) -> None:
        """
        A missing generated catalog points the user at the build command.
        """
        with self.assertRaises(OteError) as raised:
            catalog.load_catalog(Path("/tmp/definitely-not-a-repo"))
        self.assertIn("catalog build", str(raised.exception))


class CatalogValidationTests(unittest.TestCase):
    """
    Tests for catalog validation failures.
    """

    def _document(self) -> dict:
        """
        Return a mutable copy of the committed catalog.
        """
        document = catalog.load_catalog(support.REPO_ROOT)
        return copy.deepcopy(document)

    def test_unknown_schema_version_fails(self) -> None:
        """
        A future catalog schema version is rejected.
        """
        document = self._document()
        document["schema_version"] = 2
        results = catalog.verify(support.REPO_ROOT, document)
        self.assertEqual(results[0]["status"], "fail")

    def test_missing_field_fails(self) -> None:
        """
        An entry without author attribution fails validation.
        """
        document = self._document()
        document["artifacts"][0].pop("author")
        failures = [result for result in catalog.verify(support.REPO_ROOT, document) if result["status"] == "fail"]
        self.assertTrue(any("author" in result["detail"] for result in failures))

    def test_duplicate_id_fails(self) -> None:
        """
        Two entries with the same type and id are rejected.
        """
        document = self._document()
        document["artifacts"].append(copy.deepcopy(document["artifacts"][0]))
        failures = [result for result in catalog.verify(support.REPO_ROOT, document) if result["status"] == "fail"]
        self.assertTrue(any("duplicate" in result["detail"] for result in failures))

    def test_missing_local_path_fails(self) -> None:
        """
        An entry pointing at a missing file is rejected.
        """
        document = self._document()
        document["artifacts"][0]["local"] = "agents/does-not-exist/AGENT.md"
        failures = [result for result in catalog.verify(support.REPO_ROOT, document) if result["status"] == "fail"]
        self.assertTrue(any("local path missing" in result["detail"] for result in failures))

    def test_counts_mismatch_fails(self) -> None:
        """
        Declared counts must match the artifact list.
        """
        document = self._document()
        document["counts"]["agent"] = 999
        results = catalog.verify(support.REPO_ROOT, document)
        self.assertTrue(any(result["check"] == "counts" and result["status"] == "fail" for result in results))


class CatalogJsonTests(unittest.TestCase):
    """
    Tests for generated file contents.
    """

    def test_registry_json_is_sorted(self) -> None:
        """
        Generated entries keep a stable order for reproducible diffs.
        """
        document = catalog.load_catalog(support.REPO_ROOT)
        keys = [(entry["type"], entry["id"]) for entry in document["artifacts"]]
        self.assertEqual(keys, sorted(keys, key=lambda item: ({"agent": 0, "skill": 1, "command": 2, "hat": 3}[item[0]], item[1])))

    def test_counts_match_artifacts(self) -> None:
        """
        The declared counts equal the grouped artifact counts.
        """
        document = catalog.load_catalog(support.REPO_ROOT)
        counts: dict[str, int] = {}
        for entry in document["artifacts"]:
            counts[entry["type"]] = counts.get(entry["type"], 0) + 1
        self.assertEqual(document["counts"], dict(sorted(counts.items())))

    def test_index_mentions_every_artifact(self) -> None:
        """
        The generated Markdown index lists every artifact id.
        """
        document = catalog.load_catalog(support.REPO_ROOT)
        index = (support.REPO_ROOT / "catalog/index.md").read_text(encoding="utf-8")
        for entry in document["artifacts"]:
            self.assertIn(f"`{entry['id']}`", index)

    def test_schema_parses(self) -> None:
        """
        The committed schema is valid JSON.
        """
        schema = json.loads((support.REPO_ROOT / "catalog/schema/entry.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["type"], "object")


if __name__ == "__main__":
    unittest.main()
