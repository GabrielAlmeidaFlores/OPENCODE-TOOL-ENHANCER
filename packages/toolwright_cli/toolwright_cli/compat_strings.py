"""
String constants for compat.py.

Side effects: none.
"""
from __future__ import annotations
from .constants import TEMPLATE_DATA_ROW
from .constants import TEMPLATE_DATA_ROW as TEMPLATE_HEADER_ROW
from .constants import TEXT_TEXT as TEXT_TEXT_2
from .constants import KEY_MCP
from .constants import KEY_TOOL

from .constants import (
    DEFAULT_ADAPTER,
    EMPTY_STRING,
    NEWLINE,
)

KEY_DISCLAIMER = 'disclaimer'

KEY_EXPERIMENTAL = 'experimental'


KEY_NO = 'no'

KEY_NOTE = 'note'


KEY_V1 = 'v1'

KEY_V2 = 'v2'

KEY_VERSIONS = 'versions'

KEY_YES = 'yes'

TEXT_AGENT_DEFINITIONS = 'Agent definitions'

TEXT_CODE_MODE = 'Code Mode'

TEXT_CODE_MODE_GROUPS_MCP_TOOLS_AND_REDUCES_SCHEMA_OVERHEAD = 'Code Mode groups MCP tools and reduces schema overhead.'

TEXT_COMMAND_FILES_AND_AGENT_TARGETS_ARE_SUPPORTED_BY_BOTH = 'Command files and agent targets are supported by both.'

TEXT_COMPACTION_CONTROLS = 'Compaction controls'

TEXT_COMPATIBILITY_MATRIX_ONLY_IT_RECORDS_SUPPORTED_FEATURES_NOT_ = 'Compatibility matrix only; it records supported features, not performance or benchmark results.'

TEXT_COST_STATISTICS_JSON = 'Cost statistics JSON'

TEXT_EXPERIMENTAL_SUBAGENT_DEPTH_IS_V2_NATIVE = 'experimental.subagent_depth is V2-native.'

TEXT_MARKDOWN_AGENTS_WITH_FRONTMATTER_ARE_READ_BY_BOTH_VERSIONS = 'Markdown agents with frontmatter are read by both versions.'

TEXT_MCP_CONFIGURATION = 'MCP configuration'

TEXT_MCP_SERVERS = 'mcp.servers'

TEXT_NATIVE_LSP_NAVIGATION = 'Native LSP navigation'

TEXT_NOTE = 'Note'

TEXT_NOT_VERIFIED = 'not verified'

TEXT_OPENCODE_STATS_COST_JSON_IS_VERIFIED_ON_2_2_7 = 'opencode stats --cost --json is verified on 2.2.7.'

TEXT_SKILLS = 'Skills'

TEXT_SLASH_COMMANDS = 'Slash commands'

TEXT_SUBAGENT_DEPTH_CONTROL = 'Subagent depth control'

TEXT_TEXT = '{}  {}  {}  {}'


TEXT_THE_SKILL_TOOL_WAS_VERIFIED_ON_V2_ONLY = 'The skill tool was verified on V2 only.'

TEXT_TOOL_OUTPUT_LIMITS = 'Tool output limits'

TEXT_V1 = 'V1'

TEXT_V1_REQUIRES_OPENCODE_EXPERIMENTAL_LSP_TOOL_V2_DOES_NOT_RUN_L = 'V1 requires OPENCODE_EXPERIMENTAL_LSP_TOOL; V2 does not run language servers.'

TEXT_V2 = 'V2'

TEXT_V2_REJECTS_THE_V1_SHAPE_SEE_AGENTS_MD_AND_ADR_001 = 'V2 rejects the V1 shape; see AGENTS.md and ADR-001.'

TEXT_VALIDATED_AGAINST_THE_V2_CONFIGURATION_LOADER = 'Validated against the V2 configuration loader.'

TEXT_FEATURE_LABEL = 'Feature'
