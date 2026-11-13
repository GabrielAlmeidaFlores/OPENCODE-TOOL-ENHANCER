"""
String constants for profiles.py.

Side effects: none.
"""
from __future__ import annotations
from .constants import KEY_DESCRIPTION
from .constants import KEY_PROFILES
from .constants import KEY_COMMANDS
from .constants import KEY_PLUGIN
from .constants import KEY_RALPH
from .constants import KEY_SKILLS
from .constants import TEXT_TEXT_3 as TEXT_TEXT
from .constants import TEXT_TEXT_3_2 as TEXT_TEXT_3
from .constants import TEXT_TEXT_4
from .constants import TEXT_TEXT_5
from .constants import TEXT_YML

from .constants import (
    DEFAULT_ADAPTER,
    EMPTY_STRING,
    ENCODING_UTF8,
    KEY_AGENTS,
    KEY_COMPONENTS,
    KEY_DETAIL,
    KEY_NAME,
    KEY_PROFILE,
    KEY_STATUS,
    SEPARATOR_COMMA_SPACE,
    STATUS_FAIL,
    STATUS_OK,
    TOOL_AST_GREP,
    TOOL_CODEGRAPH,
    TOOL_SERENA,
)







KEY_STANDARD = 'standard'

TEXT_A_Z_S = '^([a-z_]+):(?:\\s*(.*))?$'

TEXT_COMPONENTS_MUST_BE_A_NON_EMPTY_LIST = '{}: components must be a non-empty list'

TEXT_COMPONENT_S = '{} component(s)'

TEXT_DESCRIPTION_IS_REQUIRED = '{}: description is required'

TEXT_DUPLICATE_COMPONENTS = '{}: duplicate components: {}'

TEXT_DUPLICATE_PROFILE_NAME = 'duplicate profile name: {}'

TEXT_LIST_ITEM_OUTSIDE_A_LIST_KEY = '{}:{}: list item outside a list key'

TEXT_MISSING_PROFILES_DIRECTORY = 'missing profiles directory: {}'

TEXT_NAME_IS_REQUIRED = '{}: name is required'

TEXT_NAME_MUST_MATCH_THE_FILE_NAME = '{}: name must match the file name ({})'

TEXT_NO_MANIFESTS_UNDER = 'no manifests under {}'

TEXT_NO_PROFILES_FOUND_UNDER = 'no profiles found under {}'


TEXT_TEXT_2 = '- '




TEXT_UNKNOWN_COMPONENTS = '{}: unknown components: {}'

TEXT_UNKNOWN_COMPONENTS_2 = 'unknown components: {}'

TEXT_UNKNOWN_PROFILE_AVAILABLE = 'unknown profile: {} (available: {})'

TEXT_UNKNOWN_PROFILE_KEY = '{}:{}: unknown profile key {}'

TEXT_UNSUPPORTED_INDENTATION = '{}:{}: unsupported indentation'

TEXT_UNSUPPORTED_PROFILE_SYNTAX = '{}:{}: unsupported profile syntax'

