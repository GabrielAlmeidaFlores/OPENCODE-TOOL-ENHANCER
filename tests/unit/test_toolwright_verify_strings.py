"""
String constants for tests/unit/test_toolwright_verify.py.

Side effects: none.
"""
from __future__ import annotations
from tests.constants import (
    KEY_FAIL,
    KEY_FAILED,
    KEY_MAX_ITERATIONS,
    KEY_MISSING,
    KEY_NOPE,
    KEY_OK,
    KEY_ONE,
    KEY_PASS,
    KEY_STATUS,
    KEY_TRUE,
    KEY_TWO,
    KEY_X,
    TEXT_MAIN,
    TEXT_TOOLWRIGHT_CONFIG_TOML,
    TEXT_UTF_8,
)

KEY_PASSED = 'passed'
KEY_SLOW = 'slow'
KEY_SRC = 'src'
KEY_TIMEOUT = 'timeout'
TEXT_COMMAND_FAILURE = 'command-failure'
TEXT_COUNTER_TXT = 'counter.txt'
TEXT_GOVERNANCE_MAX_ITERATIONS_5 = '[governance]\nmax_iterations = 5\n'
TEXT_INPUT_TXT = 'input.txt'
TEXT_MISSING_COMMAND = 'missing-command'
TEXT_SRC_KEEP_TXT = 'src/keep.txt'
TEXT_SRC_PYCACHE = 'src/__pycache__'
TEXT_SRC_PYCACHE_DROP_PYC = 'src/__pycache__/drop.pyc'
TEXT_TEXT = '[]'
TEXT_TOOLWRIGHT_CACHE_VERIFY_CACHE_JSON = '.toolwright/cache/verify/cache.json'
TEXT_VERIFY_CHECKS_BAD_NAME_COMMAND_TRUE = '[verify.checks."bad name"]\ncommand = "true"\n'
TEXT_VERIFY_CHECKS_CACHE_COMMAND_SH_C_ECHO_X_COUNTER_TXT_INPUTS_S = '[verify.checks.cache]\ncommand = "sh -c \'echo x >> counter.txt\'"\ninputs = ["src"]\n'
TEXT_VERIFY_CHECKS_CACHE_COMMAND_TRUE_GOVERNANCE_VALIDATOR_MODE_L = '[verify.checks.cache]\ncommand = "true"\n\n[governance]\nvalidator_mode = "loose"\n'
TEXT_VERIFY_CHECKS_CACHE_COMMAND_TRUE_INPUTS_ETC_PASSWD = '[verify.checks.cache]\ncommand = "true"\ninputs = ["/etc/passwd"]\n'
TEXT_VERIFY_CHECKS_CACHE_COMMAND_TRUE_INPUTS_MISSING_TXT = '[verify.checks.cache]\ncommand = "true"\ninputs = ["missing.txt"]\n'
TEXT_VERIFY_CHECKS_OK_TIMEOUT_5 = '[verify.checks.ok]\ntimeout = 5\n'
TEXT_VERIFY_TIMEOUT_30_VERIFY_CHECKS_OK_COMMAND_TRUE_GOVERNANCE_M = '[verify]\ntimeout = 30\n\n[verify.checks.ok]\ncommand = "true"\n\n[governance]\nmax_iterations = 5\n'
