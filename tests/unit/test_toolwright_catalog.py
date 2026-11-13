"""
Unit tests for the verified artifact catalog.
"""
from __future__ import annotations
from tests.unit.test_toolwright_catalog_strings import (
    TEXT_BACKTICK,
)
from tests.unit.test_toolwright_catalog_strings import (
    KEY_AGENT,
    KEY_ARTIFACTS,
    KEY_AUTHOR,
    KEY_CHECK,
    KEY_COMMAND,
    KEY_COUNTS,
    KEY_DETAIL,
    KEY_DUPLICATE,
    KEY_FAIL,
    KEY_HAT,
    KEY_ID,
    KEY_LOCAL,
    KEY_OBJECT,
    KEY_OK,
    KEY_RUN_CATALOG_BUILDER,
    KEY_SCHEMA_VERSION,
    KEY_SECURITY,
    KEY_SKILL,
    KEY_STATUS,
    KEY_TYPE,
    TEXT_AGENTS_DOES_NOT_EXIST_AGENT_MD,
    TEXT_CATALOG_BUILD,
    TEXT_CATALOG_INDEX_MD,
    TEXT_CATALOG_SCHEMA_ENTRY_SCHEMA_JSON,
    TEXT_LOCAL_PATH_MISSING,
    TEXT_MAIN,
    TEXT_MIT,
    TEXT_NO_SUCH_ARTIFACT,
    TEXT_TEXT,
    TEXT_TMP_DEFINITELY_NOT_A_REPO,
    TEXT_UTF_8,
)

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
        self.assertEqual(document[KEY_SCHEMA_VERSION], 1)
        self.assertIn(KEY_ARTIFACTS, document)
        self.assertGreater(len(document[KEY_ARTIFACTS]), 0)

    def test_verify_passes(self) -> None:
        document = catalog.load_catalog(support.REPO_ROOT)
        results = catalog.verify_catalog(support.REPO_ROOT, document)
        failures = [result for result in results if result[KEY_STATUS] == KEY_FAIL]
        self.assertEqual(failures, [])

    def test_search_matches_metadata(self) -> None:
        document = catalog.load_catalog(support.REPO_ROOT)
        self.assertTrue(catalog.search_catalog(document, KEY_SECURITY))
        self.assertTrue(catalog.search_catalog(document, TEXT_MIT))
        self.assertEqual(catalog.search_catalog(document, TEXT_NO_SUCH_ARTIFACT), [])
        self.assertEqual(catalog.search_catalog(document, TEXT_TEXT), [])

    def test_missing_catalog_is_an_error(self) -> None:
        with self.assertRaises(ToolWrightError) as raised:
            catalog.load_catalog(Path(TEXT_TMP_DEFINITELY_NOT_A_REPO))
        self.assertIn(TEXT_CATALOG_BUILD, str(raised.exception))


class CatalogValidationTests(unittest.TestCase):

    def _document(self) -> dict:
        document = catalog.load_catalog(support.REPO_ROOT)
        return copy.deepcopy(document)

    def test_unknown_schema_version_fails(self) -> None:
        document = self._document()
        document[KEY_SCHEMA_VERSION] = 2
        results = catalog.verify_catalog(support.REPO_ROOT, document)
        self.assertEqual(results[0][KEY_STATUS], KEY_FAIL)

    def test_missing_field_fails(self) -> None:
        document = self._document()
        document[KEY_ARTIFACTS][0].pop(KEY_AUTHOR)
        failures = [result for result in catalog.verify_catalog(support.REPO_ROOT, document) if result[KEY_STATUS] == KEY_FAIL]
        self.assertTrue(any(KEY_AUTHOR in result[KEY_DETAIL] for result in failures))

    def test_duplicate_id_fails(self) -> None:
        document = self._document()
        document[KEY_ARTIFACTS].append(copy.deepcopy(document[KEY_ARTIFACTS][0]))
        failures = [result for result in catalog.verify_catalog(support.REPO_ROOT, document) if result[KEY_STATUS] == KEY_FAIL]
        self.assertTrue(any(KEY_DUPLICATE in result[KEY_DETAIL] for result in failures))

    def test_missing_local_path_fails(self) -> None:
        document = self._document()
        document[KEY_ARTIFACTS][0][KEY_LOCAL] = TEXT_AGENTS_DOES_NOT_EXIST_AGENT_MD
        failures = [result for result in catalog.verify_catalog(support.REPO_ROOT, document) if result[KEY_STATUS] == KEY_FAIL]
        self.assertTrue(any(TEXT_LOCAL_PATH_MISSING in result[KEY_DETAIL] for result in failures))

    def test_counts_mismatch_fails(self) -> None:
        document = self._document()
        document[KEY_COUNTS][KEY_AGENT] = 999
        results = catalog.verify_catalog(support.REPO_ROOT, document)
        self.assertTrue(any(result[KEY_CHECK] == KEY_COUNTS and result[KEY_STATUS] == KEY_FAIL for result in results))


class CatalogDriftTests(unittest.TestCase):
    def test_drift_uses_the_builder(self) -> None:
        with mock.patch.object(catalog, KEY_RUN_CATALOG_BUILDER, return_value=(0, KEY_OK)) as builder:
            result = catalog.check_catalog_drift(support.REPO_ROOT)
        self.assertEqual(result[KEY_STATUS], KEY_OK)
        builder.assert_called_once()


class CatalogJsonTests(unittest.TestCase):

    def test_registry_json_is_sorted(self) -> None:
        document = catalog.load_catalog(support.REPO_ROOT)
        keys = [(entry[KEY_TYPE], entry[KEY_ID]) for entry in document[KEY_ARTIFACTS]]
        self.assertEqual(keys, sorted(keys, key=lambda item: ({KEY_AGENT: 0, KEY_SKILL: 1, KEY_COMMAND: 2, KEY_HAT: 3}[item[0]], item[1])))

    def test_counts_match_artifacts(self) -> None:
        document = catalog.load_catalog(support.REPO_ROOT)
        counts: dict[str, int] = {}
        for entry in document[KEY_ARTIFACTS]:
            counts[entry[KEY_TYPE]] = counts.get(entry[KEY_TYPE], 0) + 1
        self.assertEqual(document[KEY_COUNTS], dict(sorted(counts.items())))

    def test_index_mentions_every_artifact(self) -> None:
        document = catalog.load_catalog(support.REPO_ROOT)
        index = (support.REPO_ROOT / TEXT_CATALOG_INDEX_MD).read_text(encoding=TEXT_UTF_8)
        for entry in document[KEY_ARTIFACTS]:
            self.assertIn(TEXT_BACKTICK + entry[KEY_ID] + TEXT_BACKTICK, index)

    def test_schema_parses(self) -> None:
        schema = json.loads((support.REPO_ROOT / TEXT_CATALOG_SCHEMA_ENTRY_SCHEMA_JSON).read_text(encoding=TEXT_UTF_8))
        self.assertEqual(schema[KEY_TYPE], KEY_OBJECT)


if __name__ == TEXT_MAIN:
    unittest.main()
