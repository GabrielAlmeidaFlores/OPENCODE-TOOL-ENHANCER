"""
String constants for pilot.py.

Side effects: none.
"""
from __future__ import annotations
from .constants import KEY_ORIGIN
from .constants import KEY_PILOT
from .constants import TEXT_VERIFICATION_COMMAND as TEXT_VERIFICATION_COMMAND_2
from .constants import FLAG_AGENT
from .constants import FLAG_FORMAT
from .constants import FLAG_STANDALONE
from .constants import KEY_AGENT
from .constants import KEY_COORDINATOR
from .constants import KEY_COST
from .constants import KEY_DRY_RUN
from .constants import KEY_GIT
from .constants import KEY_INPUT_TOKENS
from .constants import KEY_JSON
from .constants import KEY_MODEL
from .constants import KEY_OPENCODE_EXIT
from .constants import KEY_OUTPUT_TOKENS
from .constants import KEY_PILOTS
from .constants import KEY_RUN
from .constants import KEY_STACK
from .constants import KEY_STEPS
from .constants import KEY_SUCCESS
from .constants import KEY_TOOL_CALLS
from .constants import KEY_TOOL_ERRORS
from .constants import KEY_VERIFICATION_EXIT
from .constants import KEY_WALL_TIME_SECONDS
from .constants import KEY_WORKSPACE
from .constants import TEXT_1
from .constants import TEXT_C
from .constants import TEXT_INVALID_TOML
from .constants import TEXT_META_JSON
from .constants import TEXT_OPENCODE_CONFIG
from .constants import TEXT_OPENCODE_OPENCODE_JSONC
from .constants import TEXT_OPENCODE_PILOT_MODEL
from .constants import TEXT_SESSION_JSONL

from .constants import (
    BASH,
    DEFAULT_ADAPTER,
    EMPTY_STRING,
    ENCODING_UTF8,
    ISO_TIMESPEC,
    KEY_ARTIFACTS,
    KEY_COMMIT,
    KEY_COMPONENTS,
    KEY_NAME,
    KEY_PROFILE,
    KEY_REPOSITORY,
    NEWLINE,
    SEPARATOR_COMMA_SPACE,
    SEPARATOR_SPACE,
)


FLAG_AUTO = '--auto'

FLAG_DEPTH = '--depth'

FLAG_DETACH = '--detach'

FLAG_FILTER_BLOB_NONE = '--filter=blob:none'


FLAG_MODEL = '--model'

FLAG_NO_CHECKOUT = '--no-checkout'



KEY_CHECKOUT = 'checkout'

KEY_CLONE = 'clone'









KEY_OPENCODE_STDERR = 'opencode_stderr'





KEY_PROMPT = 'prompt'


KEY_SETUP_COMMAND = 'setup_command'


KEY_STARTED_AT = 'started_at'





KEY_VERIFICATION_COMMAND = 'verification_command'





TEXT_BASH_LC = 'bash -lc {}'


TEXT_COMMAND_EXIT = 'command: {}\nexit: {}\n\n{}\n{}\n'

TEXT_CONFIGS_PILOTS_PILOTS_TOML = 'configs/pilots/pilots.toml'

TEXT_GIT_CLONE_NO_CHECKOUT_FILTER_BLOB_NONE = 'git clone --no-checkout --filter=blob:none {} {}'

TEXT_GIT_C_CHECKOUT_DETACH_FETCH_HEAD = 'git -C {} checkout --detach FETCH_HEAD'

TEXT_GIT_C_FETCH_DEPTH_1_ORIGIN = 'git -C {} fetch --depth 1 origin {}'

TEXT_GIT_FAILED = 'git {} failed: {}'


TEXT_IS_REQUIRED_FOR_A_REAL_PILOT_RUN = '{} is required for a real pilot run'

TEXT_LC = '-lc'


TEXT_MISSING_PILOTS_NAME_TABLES = '{}: missing [pilots.<name>] tables'




TEXT_OPENCODE_STANDALONE_RUN_AGENT_MODEL_AUTO_FORMAT_JSON_PROMPT = 'opencode --standalone run --agent {} --model {} --auto --format json <prompt>'

TEXT_PILOTS_MISSING = '{}: pilots.{} missing {}'

TEXT_PILOTS_MUST_BE_A_TABLE = '{}: pilots.{} must be a table'

TEXT_PILOT_CONFIGURATION_NOT_FOUND = 'pilot configuration not found: {}'

TEXT_PILOT_RUN_PILOT_REPOSITORY_COMMIT_MODEL_OPENCODE_EXIT_SUCCES = '# Pilot Run\n\n- Pilot: {}\n- Repository: {}\n- Commit: {}\n- Model: {}\n- OpenCode exit: {}\n- Success: {}\n- Verification exit: {}\n- Cost: ${:.6f}\n- Tokens: {} input, {} output\n- Tool calls: {} ({} errors)\n- Wall time: {}s\n\nSuccess requires both the OpenCode run and the verification command to exit zero. Rework and human intervention must be recorded separately.\n'

TEXT_PILOT_SETUP_FAILED = 'pilot setup failed: {}'

TEXT_PROVIDER_MODEL = '<provider/model>'

TEXT_PWD = 'PWD'


TEXT_SETUP_COMMAND = '<setup command>'

TEXT_SUMMARY_MD = 'summary.md'

TEXT_TOOLWRIGHT_INSTALL_PROFILE_TARGET_APPLY = 'toolwright install --profile {} --target {} --apply'

TEXT_TOOLWRIGHT_PILOT = 'toolwright-pilot-{}-'

TEXT_UNKNOWN_PILOT_AVAILABLE = 'unknown pilot: {} (available: {})'

TEXT_VERIFICATION_COMMAND = '<verification command>'


TEXT_VERIFICATION_LOG = 'verification.log'

TEXT_WORKSPACE_ALREADY_CONTAINS_A_CLONE = 'workspace already contains a clone: {}'
