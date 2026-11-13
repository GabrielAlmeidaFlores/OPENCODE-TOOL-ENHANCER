"""
String constants for tests/integration/test_entrypoints.py.

Side effects: none.
"""
from __future__ import annotations
from tests.constants import (
    FLAG_DRY_RUN,
    FLAG_ONLY,
    FLAG_TARGET,
    KEY_AGENTS,
    KEY_BASELINE,
    KEY_BASH,
    KEY_NONSENSE,
    KEY_PROJECT,
    TEXT_MAIN,
    TEXT_OK,
    TEXT_SCRIPTS_INSTALLATION_INSTALL_SH,
    TEXT_SCRIPTS_VALIDATION_VALIDATE_CONFIG_PY,
)

FLAG_ARM = '--arm'
FLAG_TASK = '--task'
KEY_PYTHON3 = 'python3'
TEXT_BENCHMARKS_HARNESS_RUN_SH = 'benchmarks/harness/run.sh'
TEXT_BENCHMARKS_TASKS = 'benchmarks/tasks'
TEXT_CHECKED_D = 'checked: \\d+'
TEXT_DEFAULT_MODE_MUST_NOT_CREATE_THE_TARGET = 'default mode must not create the target'
TEXT_HOME = 'HOME'
TEXT_JSON = '*.json'
TEXT_MISSING_JSON = 'missing.json'
TEXT_NO_BENCHMARK_TASKS_FOUND = 'no benchmark tasks found'
TEXT_PATH = 'PATH'
TEXT_SCRIPTS_VALIDATION_VALIDATE_SH = 'scripts/validation/validate.sh'
TEXT_TASK_NOT_FOUND = 'task not found'
TEXT_TOOLWRIGHT_INSTALL = 'toolwright-install-'
TEXT_UNKNOWN_ARM = 'unknown arm'
TEXT_WOULD_RUN = 'would run:'
TEXT_PATH_SUFFIX = ':/usr/bin:/bin'
from tests.constants import TEXT_TASK_ERROR
