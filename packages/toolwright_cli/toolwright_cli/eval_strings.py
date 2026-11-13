"""
String constants for eval.py.

Side effects: none.
"""
from __future__ import annotations
from .constants import KEY_CATALOG
from .constants import KEY_DESCRIPTION
from .constants import KEY_GOVERNANCE
from .constants import KEY_PROFILES
from .constants import KEY_VALIDATOR
from .constants import TEXT_SCRIPTS_VALIDATION_VALIDATE_CONFIG_PY
from .constants import KEY_CONTRACTS
from .constants import TEXT_INVALID_JSON

from .constants import (
    EMPTY_STRING,
    ENCODING_UTF8,
    KEY_ARTIFACTS,
    KEY_DETAIL,
    KEY_EXIT_CODE,
    KEY_ID,
    KEY_SCHEMA_VERSION,
    KEY_STATUS,
    SEPARATOR_COMMA_SPACE,
    STATUS_FAIL,
    STATUS_OK,
)

KEY_CASES = 'cases'




KEY_EXPECTED = 'expected'




TEXT_ARTIFACT_S_VALID = '{} artifact(s) valid'

TEXT_CASES_MUST_BE_A_JSON_OBJECT = '{}: cases must be a JSON object'

TEXT_CASES_MUST_BE_A_NON_EMPTY_LIST = '{}: cases must be a non-empty list'

TEXT_CATALOG_FAILURE_S = '{} catalog failure(s)'

TEXT_CONTRACT_FAILURE_S = '{} contract failure(s)'

TEXT_CONTRACT_S_VALID = '{} contract(s) valid'

TEXT_EVALUATION_CASES_NOT_FOUND = 'evaluation cases not found: {}'

TEXT_EXIT = 'exit {}'

TEXT_EXPECTED_ARTIFACTS_FOUND = 'expected {} artifacts, found {}'

TEXT_EXPECTED_CONTRACTS_FOUND = 'expected {} contracts, found {}'

TEXT_EXPECTED_PROFILES_FOUND = 'expected {} profiles, found {}'


TEXT_INVALID_PROFILE_S = '{} invalid profile(s)'

TEXT_PROFILE_S_VALID = '{} profile(s) valid'


TEXT_TESTS_EVALS_CASES_JSON = 'tests/evals/cases.json'

TEXT_UNKNOWN_EVALUATION_CASES = 'unknown evaluation cases: {}'

TEXT_UNKNOWN_EVALUATION_CASE_R = '{}: unknown evaluation case {!r}'

TEXT_UNSUPPORTED_SCHEMA_VERSION = '{}: unsupported schema_version'

TEXT_VALIDATOR_PASSED = 'validator passed'
