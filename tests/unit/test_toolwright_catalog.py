"""
Unit tests for the verified artifact catalog.
"""
from __future__ import annotations

import copy
import json
import unittest
from unittest import mock
from pathlib import Path

from tests import support

from toolwright_cli import catalog
from toolwright_cli.paths import ToolWrightError


class CatalogRepositoryTests(unittest.TestCase):

    def test_catalog_loads(self) -> None:
        document = catalog.load_catalog(support.REPO_ROOT)
        self.assertEqual(document["schema_version"], 1)
        self.assertIn("artifacts", document)
        self.assertGreater(len(document["artifacts"]), 0)

    def test_verify_passes(self) -> None:
        document = catalog.load_catalog(support.REPO_ROOT)
        results = catalog.verify_catalog(support.REPO_ROOT, document)
        failures = [result for result in results if result["status"] == "fail"]
        self.assertEqual(failures, [])

    def test_search_matches_metadata(self) -> None:
        document = catalog.load_catalog(support.REPO_ROOT)
        self.assertTrue(catalog.search_catalog(document, "security"))
        self.assertTrue(catalog.search_catalog(document, "MIT"))
        self.assertEqual(catalog.search_catalog(document, "no-such-artifact"), [])
        self.assertEqual(catalog.search_catalog(document, "   "), [])

    def test_missing_catalog_is_an_error(self) -> None:
        with self.assertRaises(ToolWrightError) as raised:
            catalog.load_catalog(Path("/tmp/definitely-not-a-repo"))
        self.assertIn("catalog build", str(raised.exception))


class CatalogValidationTests(unittest.TestCase):

    def _document(self) -> dict:
        document = catalog.load_catalog(support.REPO_ROOT)
        return copy.deepcopy(document)

    def test_unknown_schema_version_fails(self) -> None:
        document = self._document()
        document["schema_version"] = 2
        results = catalog.verify_catalog(support.REPO_ROOT, document)
        self.assertEqual(results[0]["status"], "fail")

    def test_missing_field_fails(self) -> None:
        document = self._document()
        document["artifacts"][0].pop("author")
        failures = [result for result in catalog.verify_catalog(support.REPO_ROOT, document) if result["status"] == "fail"]
        self.assertTrue(any("author" in result["detail"] for result in failures))

    def test_duplicate_id_fails(self) -> None:
        document = self._document()
        document["artifacts"].append(copy.deepcopy(document["artifacts"][0]))
        failures = [result for result in catalog.verify_catalog(support.REPO_ROOT, document) if result["status"] == "fail"]
        self.assertTrue(any("duplicate" in result["detail"] for result in failures))

    def test_missing_local_path_fails(self) -> None:
        document = self._document()
        document["artifacts"][0]["local"] = "agents/does-not-exist/AGENT.md"
        failures = [result for result in catalog.verify_catalog(support.REPO_ROOT, document) if result["status"] == "fail"]
        self.assertTrue(any("local path missing" in result["detail"] for result in failures))

    def test_counts_mismatch_fails(self) -> None:
        document = self._document()
        document["counts"]["agent"] = 999
        results = catalog.verify_catalog(support.REPO_ROOT, document)
        self.assertTrue(any(result["check"] == "counts" and result["status"] == "fail" for result in results))


class CatalogDriftTests(unittest.TestCase):
    def test_drift_uses_the_builder(self) -> None:
        with mock.patch.object(catalog, "run_catalog_builder", return_value=(0, "ok")) as builder:
            result = catalog.check_catalog_drift(support.REPO_ROOT)
        self.assertEqual(result["status"], "ok")
        builder.assert_called_once()


class CatalogJsonTests(unittest.TestCase):

    def test_registry_json_is_sorted(self) -> None:
        document = catalog.load_catalog(support.REPO_ROOT)
        keys = [(entry["type"], entry["id"]) for entry in document["artifacts"]]
        self.assertEqual(keys, sorted(keys, key=lambda item: ({"agent": 0, "skill": 1, "command": 2, "hat": 3}[item[0]], item[1])))

    def test_counts_match_artifacts(self) -> None:
        document = catalog.load_catalog(support.REPO_ROOT)
        counts: dict[str, int] = {}
        for entry in document["artifacts"]:
            counts[entry["type"]] = counts.get(entry["type"], 0) + 1
        self.assertEqual(document["counts"], dict(sorted(counts.items())))

    def test_index_mentions_every_artifact(self) -> None:
        document = catalog.load_catalog(support.REPO_ROOT)
        index = (support.REPO_ROOT / "catalog/index.md").read_text(encoding="utf-8")
        for entry in document["artifacts"]:
            self.assertIn(f"`{entry['id']}`", index)

    def test_schema_parses(self) -> None:
        schema = json.loads((support.REPO_ROOT / "catalog/schema/entry.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["type"], "object")


if __name__ == "__main__":
    unittest.main()
