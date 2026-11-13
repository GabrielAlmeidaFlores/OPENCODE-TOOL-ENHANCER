"""
Deterministic evaluation cases for ``toolwright eval``.

Public API: :func:`load_cases` and :func:`run_evaluation_cases`.

Cases live in ``tests/evals/cases.json`` and exercise repository invariants
that must hold without a model. No network access and no paid calls occur.
"""
from __future__ import annotations
from .eval_strings import (
    EMPTY_STRING,
    ENCODING_UTF8,
    KEY_ARTIFACTS,
    KEY_CASES,
    KEY_CATALOG,
    KEY_CONTRACTS,
    KEY_DESCRIPTION,
    KEY_DETAIL,
    KEY_EXIT_CODE,
    KEY_EXPECTED,
    KEY_GOVERNANCE,
    KEY_ID,
    KEY_PROFILES,
    KEY_SCHEMA_VERSION,
    KEY_STATUS,
    KEY_VALIDATOR,
    SEPARATOR_COMMA_SPACE,
    STATUS_FAIL,
    STATUS_OK,
    TEXT_ARTIFACT_S_VALID,
    TEXT_CASES_MUST_BE_A_JSON_OBJECT,
    TEXT_CASES_MUST_BE_A_NON_EMPTY_LIST,
    TEXT_CATALOG_FAILURE_S,
    TEXT_CONTRACT_FAILURE_S,
    TEXT_CONTRACT_S_VALID,
    TEXT_EVALUATION_CASES_NOT_FOUND,
    TEXT_EXIT,
    TEXT_EXPECTED_ARTIFACTS_FOUND,
    TEXT_EXPECTED_CONTRACTS_FOUND,
    TEXT_EXPECTED_PROFILES_FOUND,
    TEXT_INVALID_JSON,
    TEXT_INVALID_PROFILE_S,
    TEXT_PROFILE_S_VALID,
    TEXT_SCRIPTS_VALIDATION_VALIDATE_CONFIG_PY,
    TEXT_TESTS_EVALS_CASES_JSON,
    TEXT_UNKNOWN_EVALUATION_CASES,
    TEXT_UNKNOWN_EVALUATION_CASE_R,
    TEXT_UNSUPPORTED_SCHEMA_VERSION,
    TEXT_VALIDATOR_PASSED,
)

import json
import sys
from pathlib import Path
from typing import Any

from . import catalog as catalog_module
from . import governance as governance_module
from .paths import ToolWrightError
from .process import capture_command
from .profiles import verify_profiles

CASES = Path(TEXT_TESTS_EVALS_CASES_JSON)
KNOWN = {KEY_PROFILES, KEY_CATALOG, KEY_GOVERNANCE, KEY_VALIDATOR}


def load_cases(root: Path) -> list[dict[str, Any]]:
    path = root / CASES
    if not path.is_file():
        raise ToolWrightError(TEXT_EVALUATION_CASES_NOT_FOUND.format(path))
    try:
        document = json.loads(path.read_text(encoding=ENCODING_UTF8))
    except json.JSONDecodeError as error:
        raise ToolWrightError(TEXT_INVALID_JSON.format(path, error)) from error
    if not isinstance(document, dict):
        raise ToolWrightError(TEXT_CASES_MUST_BE_A_JSON_OBJECT.format(path))
    if document.get(KEY_SCHEMA_VERSION) != 1:
        raise ToolWrightError(TEXT_UNSUPPORTED_SCHEMA_VERSION.format(path))
    cases = document.get(KEY_CASES)
    if not isinstance(cases, list) or not cases:
        raise ToolWrightError(TEXT_CASES_MUST_BE_A_NON_EMPTY_LIST.format(path))
    for case in cases:
        if not isinstance(case, dict) or case.get(KEY_ID) not in KNOWN:
            raise ToolWrightError(TEXT_UNKNOWN_EVALUATION_CASE_R.format(path, case))
    return cases


def build_evaluation_result(identifier: str, description: str, status: str, detail: str) -> dict[str, str]:
    return {KEY_ID: identifier, KEY_DESCRIPTION: description, KEY_STATUS: status, KEY_DETAIL: detail}


def _evaluate(case: dict[str, Any], root: Path) -> dict[str, str]:
    identifier = str(case[KEY_ID])
    description = str(case.get(KEY_DESCRIPTION, EMPTY_STRING))
    expected = case.get(KEY_EXPECTED, {})
    if identifier == KEY_PROFILES:
        results = verify_profiles(root)
        failures = [result for result in results if result[KEY_STATUS] == STATUS_FAIL]
        if failures:
            return build_evaluation_result(identifier, description, STATUS_FAIL, TEXT_INVALID_PROFILE_S.format(len(failures)))
        if KEY_PROFILES in expected and len(results) != expected[KEY_PROFILES]:
            return build_evaluation_result(identifier, description, STATUS_FAIL, TEXT_EXPECTED_PROFILES_FOUND.format(expected[KEY_PROFILES], len(results)))
        return build_evaluation_result(identifier, description, STATUS_OK, TEXT_PROFILE_S_VALID.format(len(results)))
    if identifier == KEY_CATALOG:
        document = catalog_module.load_catalog(root)
        results = catalog_module.verify_catalog(root, document)
        failures = [result for result in results if result[KEY_STATUS] == STATUS_FAIL]
        if failures:
            return build_evaluation_result(identifier, description, STATUS_FAIL, TEXT_CATALOG_FAILURE_S.format(len(failures)))
        count = len(document.get(KEY_ARTIFACTS, []))
        if KEY_ARTIFACTS in expected and count != expected[KEY_ARTIFACTS]:
            return build_evaluation_result(identifier, description, STATUS_FAIL, TEXT_EXPECTED_ARTIFACTS_FOUND.format(expected[KEY_ARTIFACTS], count))
        return build_evaluation_result(identifier, description, STATUS_OK, TEXT_ARTIFACT_S_VALID.format(count))
    if identifier == KEY_GOVERNANCE:
        results = governance_module.load_agent_contracts(root)
        failures = [result for result in results if result[KEY_STATUS] == STATUS_FAIL]
        if failures:
            return build_evaluation_result(identifier, description, STATUS_FAIL, TEXT_CONTRACT_FAILURE_S.format(len(failures)))
        if KEY_CONTRACTS in expected and len(results) != expected[KEY_CONTRACTS]:
            return build_evaluation_result(identifier, description, STATUS_FAIL, TEXT_EXPECTED_CONTRACTS_FOUND.format(expected[KEY_CONTRACTS], len(results)))
        return build_evaluation_result(identifier, description, STATUS_OK, TEXT_CONTRACT_S_VALID.format(len(results)))
    script = root / TEXT_SCRIPTS_VALIDATION_VALIDATE_CONFIG_PY
    code, stdout, stderr = capture_command([sys.executable, str(script)], cwd=root, timeout=300)
    expected_code = int(expected.get(KEY_EXIT_CODE, 0))
    if code != expected_code:
        detail = (stderr or stdout or TEXT_EXIT.format(code)).splitlines()[0]
        return build_evaluation_result(identifier, description, STATUS_FAIL, detail)
    return build_evaluation_result(identifier, description, STATUS_OK, TEXT_VALIDATOR_PASSED)


def run_evaluation_cases(root: Path, only: list[str] | None = None) -> list[dict[str, str]]:
    cases = load_cases(root)
    selected = set(only) if only else None
    unknown = selected.difference(KNOWN) if selected else set()
    if unknown:
        raise ToolWrightError(TEXT_UNKNOWN_EVALUATION_CASES.format(SEPARATOR_COMMA_SPACE.join(sorted(unknown))))
    results: list[dict[str, str]] = []
    for case in cases:
        if selected and case[KEY_ID] not in selected:
            continue
        try:
            results.append(_evaluate(case, root))
        except ToolWrightError as error:
            results.append(
                build_evaluation_result(str(case[KEY_ID]), str(case.get(KEY_DESCRIPTION, EMPTY_STRING)), STATUS_FAIL, str(error))
            )
    return results
