"""
String constants for verify.py.

Side effects: none.
"""
from __future__ import annotations
from .constants import KEY_GOVERNANCE
from .constants import KEY_ASCII
from .constants import KEY_NODE_MODULES
from .constants import TEXT_DS_STORE
from .constants import TEXT_PYC
from .constants import TEXT_PYCACHE
from .constants import TEXT_PYO
from .constants import TEXT_TEXT_2_3 as TEXT_TEXT_2
from .constants import KEY_ADVISORY
from .constants import KEY_CHECKS
from .constants import KEY_COMMAND
from .constants import KEY_EXIT_CODE
from .constants import KEY_PASSED
from .constants import KEY_SECURITY
from .constants import KEY_STDERR
from .constants import KEY_STDOUT
from .constants import KEY_VALIDATOR_MODE
from .constants import KEY_VERIFY
from .constants import TEXT_INVALID_TOML
from .constants import TEXT_TOOLWRIGHT_CONFIG_TOML

from .constants import (
    EMPTY_STRING,
    ENCODING_UTF8,
    ISO_TIMESPEC,
    KEY_SCHEMA_VERSION,
    KEY_STATUS,
    KEY_TYPE,
    NEWLINE,
    SEPARATOR_COMMA_SPACE,
)







KEY_INPUTS = 'inputs'

KEY_KEY = 'key'

KEY_LINT = 'lint'


KEY_OFF = 'off'

KEY_PASS = 'pass'


KEY_PERMISSION = 'permission'




KEY_STRICT = 'strict'

KEY_TEST = 'test'

KEY_TIMEOUT = 'timeout'

KEY_TOTAL = 'total'

KEY_VALIDATE = 'validate'



TEXT_A_Z0_9_A_Z0_9 = '^[a-z0-9][a-z0-9_-]*$'

TEXT_CACHE_INPUT_DOES_NOT_EXIST = 'cache input does not exist: {}'

TEXT_COMMAND_FAILURE = 'command-failure'

TEXT_CONFIGURATION_MUST_BE_A_TABLE = '{}: configuration must be a table'


TEXT_EGG_INFO = '.egg-info'

TEXT_GOVERNANCE_MUST_BE_A_TABLE = '{}: governance must be a table'

TEXT_GOVERNANCE_VALIDATOR_MODE_MUST_BE_OFF_ADVISORY_OR_STRICT = '{}: governance.validator_mode must be off, advisory, or strict'

TEXT_INVALID_CHECK_NAME = 'invalid check name: {}'


TEXT_JSON = '{}.json'

TEXT_LINT_FAILURE = 'lint-failure'

TEXT_MISSING_COMMAND = 'missing-command'

TEXT_MISSING_VERIFICATION_CONFIG = 'missing verification config: {}'

TEXT_MISSING_VERIFY_CHECKS_NAME_TABLES = '{}: missing [verify.checks.<name>] tables'

TEXT_MISSING_VERIFY_TABLE = '{}: missing [verify] table'




TEXT_SECURITY_FAILURE = 'security-failure'

TEXT_TEST_FAILURE = 'test-failure'

TEXT_TEXT = '..'


TEXT_TIMED_OUT_AFTER_S = 'timed out after {}s'

TEXT_TOOLWRIGHT_CACHE_VERIFY = '.toolwright/cache/verify'


TEXT_TYPE_FAILURE = 'type-failure'

TEXT_UNKNOWN_CHECKS = 'unknown checks: {}'

TEXT_VALIDATION_FAILURE = 'validation-failure'

TEXT_VERIFY_CHECKS_COMMAND_IS_REQUIRED = '{}: verify.checks.{}.command is required'

TEXT_VERIFY_CHECKS_INPUTS_MUST_BE_A_LIST_OF_PATHS = '{}: verify.checks.{}.inputs must be a list of paths'

TEXT_VERIFY_CHECKS_INPUTS_MUST_STAY_INSIDE_THE_REPOSITORY = '{}: verify.checks.{}.inputs must stay inside the repository'

TEXT_VERIFY_CHECKS_MUST_BE_A_TABLE = '{}: verify.checks.{} must be a table'

TEXT_VERIFY_CHECKS_TIMEOUT_MUST_BE_POSITIVE = '{}: verify.checks.{}.timeout must be positive'

TEXT_VERIFY_TIMEOUT_MUST_BE_A_POSITIVE_NUMBER = '{}: verify.timeout must be a positive number'
