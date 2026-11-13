"""
String constants for doctor.py.

Side effects: none.
"""
from __future__ import annotations
from .constants import KEY_VALIDATOR
from .constants import TEXT_AGENTS_COORDINATOR_AGENT_MD
from .constants import TEXT_SCRIPTS_VALIDATION_VALIDATE_CONFIG_PY
from .constants import TEXT_VERSION
from .constants import KEY_COMMANDS
from .constants import KEY_LIST
from .constants import KEY_RALPH
from .constants import KEY_SKILLS
from .constants import TEXT_CONFIGS_OPENCODE_OPENCODE_JSONC
from .constants import TEXT_CONFIGS_RALPH_HATS
from .constants import TEXT_MD_2 as TEXT_MD
from .constants import TEXT_MISSING_2
from .constants import TEXT_SCRIPTS_INSTALLATION_INSTALL_SH
from .constants import TEXT_SKILL_MD
from .constants import TEXT_YML
from .constants import FLAG_STANDALONE
from .constants import FLAG_VERSION
from .constants import KEY_AGENTS
from .constants import KEY_CHECKS
from .constants import KEY_GIT
from .constants import KEY_MCP
from .constants import KEY_STATE
from .constants import TEXT_AGENT_MD
from .constants import TEXT_OPENCODE_CONFIG
from .constants import TEXT_OPENCODE_OPENCODE_JSONC

from .constants import (
    DEFAULT_ADAPTER,
    KEY_ARTIFACTS,
    KEY_DETAIL,
    KEY_ID,
    KEY_LOCK,
    KEY_PATH,
    KEY_REPOSITORY,
    KEY_STATUS,
    KEY_SUMMARY,
    NEWLINE,
    SEPARATOR_COMMA_SPACE,
    STATUS_OK,
    STATUS_WARN,
    TOOL_AST_GREP,
    TOOL_CODEGRAPH,
    TOOL_SERENA,
)









KEY_NODE = 'node'

KEY_PYTHON = 'python'


KEY_RG = 'rg'




TEXT_AGENTS_COMMANDS_SKILLS_HATS = '{} agents, {} commands, {} skills, {} hats'

TEXT_AGENTS_COMMANDS_SKILLS_HATS_2 = 'agents={} commands={} skills={} hats={}'



TEXT_CHECKED = 'checked: {}'

TEXT_CHECKED_D = 'checked: (\\d+)'



TEXT_DOCS_PROVENANCE_REGISTRY_YML = 'docs/provenance/registry.yml'

TEXT_D_D_D = '(\\d+)\\.(\\d+)\\.(\\d+)'

TEXT_ERROR = 'ERROR'

TEXT_FILE_S_DIFFER_E_G = '{} file(s) differ, e.g. {} ({})'

TEXT_IS_NOT_A_DIRECTORY = '{} is not a directory'

TEXT_IS_OLDER_THAN_3_11 = '{} is older than 3.11'

TEXT_IS_V1_THIS_PROFILE_REQUIRES_V2 = '{} is V1; this profile requires V2'

TEXT_LINE_S_REPORTED = '{} line(s) reported'

TEXT_MANAGED_FILE_S_MATCH = '{} managed file(s) match'

TEXT_MCP_LIST_FAILED = 'mcp list failed'


TEXT_MISSING = 'missing: {}'


TEXT_NOT_FOUND_ON_PATH = 'not found on PATH'

TEXT_NO_OPENCODE_OPENCODE_JSONC_IN_THE_TARGET_SKIPPING = 'no .opencode/opencode.jsonc in the target; skipping'

TEXT_NO_TOOLWRIGHT_LOCK_JSON_IN_THE_TARGET_NOTHING_INSTALLED_BY_T = 'no toolwright.lock.json in the target; nothing installed by toolwright yet'

TEXT_NO_TOOLWRIGHT_STATE_JSON_YET = 'no .toolwright/state.json yet'



TEXT_OPENCODE_VERSION_FAILED = 'opencode --version failed'




TEXT_SKIPPED_BY_NO_MCP = 'skipped by --no-mcp'

TEXT_TEXT = '{}.{}.{}'

TEXT_VALIDATOR_FAILED = 'validator failed'
