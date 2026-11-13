"""
OpenCode V1 and V2 compatibility matrix.

Public API: :data:`MATRIX`, :func:`as_compatibility_dict`, and :func:`render_text`.

The matrix records only behaviour documented in ``docs/decisions/ADR-001`` or
verified in this repository. Cells that were not verified are marked as such.

Side effects: none.
"""
from __future__ import annotations
from .constants import KEY_FEATURE
from .constants import KEY_FEATURES
from .compat_strings import TEXT_FEATURE_LABEL
from .compat_strings import TEMPLATE_DATA_ROW
from .compat_strings import TEMPLATE_HEADER_ROW
from .compat_strings import (
    DEFAULT_ADAPTER,
    EMPTY_STRING,
    KEY_DISCLAIMER,
    KEY_EXPERIMENTAL,
    KEY_MCP,
    KEY_NO,
    KEY_NOTE,
    KEY_TOOL,
    KEY_V1,
    KEY_V2,
    KEY_VERSIONS,
    KEY_YES,
    NEWLINE,
    TEXT_AGENT_DEFINITIONS,
    TEXT_CODE_MODE,
    TEXT_CODE_MODE_GROUPS_MCP_TOOLS_AND_REDUCES_SCHEMA_OVERHEAD,
    TEXT_COMMAND_FILES_AND_AGENT_TARGETS_ARE_SUPPORTED_BY_BOTH,
    TEXT_COMPACTION_CONTROLS,
    TEXT_COMPATIBILITY_MATRIX_ONLY_IT_RECORDS_SUPPORTED_FEATURES_NOT_,
    TEXT_COST_STATISTICS_JSON,
    TEXT_EXPERIMENTAL_SUBAGENT_DEPTH_IS_V2_NATIVE,
    TEXT_MARKDOWN_AGENTS_WITH_FRONTMATTER_ARE_READ_BY_BOTH_VERSIONS,
    TEXT_MCP_CONFIGURATION,
    TEXT_MCP_SERVERS,
    TEXT_NATIVE_LSP_NAVIGATION,
    TEXT_NOTE,
    TEXT_NOT_VERIFIED,
    TEXT_OPENCODE_STATS_COST_JSON_IS_VERIFIED_ON_2_2_7,
    TEXT_SKILLS,
    TEXT_SLASH_COMMANDS,
    TEXT_SUBAGENT_DEPTH_CONTROL,
    TEXT_TEXT,
    TEXT_TEXT_2,
    TEXT_THE_SKILL_TOOL_WAS_VERIFIED_ON_V2_ONLY,
    TEXT_TOOL_OUTPUT_LIMITS,
    TEXT_V1,
    TEXT_V1_REQUIRES_OPENCODE_EXPERIMENTAL_LSP_TOOL_V2_DOES_NOT_RUN_L,
    TEXT_V2,
    TEXT_V2_REJECTS_THE_V1_SHAPE_SEE_AGENTS_MD_AND_ADR_001,
    TEXT_VALIDATED_AGAINST_THE_V2_CONFIGURATION_LOADER,
)

from typing import Any

DISCLAIMER = TEXT_COMPATIBILITY_MATRIX_ONLY_IT_RECORDS_SUPPORTED_FEATURES_NOT_

MATRIX: tuple[dict[str, str], ...] = (
    {
        KEY_FEATURE: TEXT_AGENT_DEFINITIONS,
        KEY_V1: KEY_YES,
        KEY_V2: KEY_YES,
        KEY_NOTE: TEXT_MARKDOWN_AGENTS_WITH_FRONTMATTER_ARE_READ_BY_BOTH_VERSIONS,
    },
    {
        KEY_FEATURE: TEXT_SLASH_COMMANDS,
        KEY_V1: KEY_YES,
        KEY_V2: KEY_YES,
        KEY_NOTE: TEXT_COMMAND_FILES_AND_AGENT_TARGETS_ARE_SUPPORTED_BY_BOTH,
    },
    {
        KEY_FEATURE: TEXT_SKILLS,
        KEY_V1: TEXT_NOT_VERIFIED,
        KEY_V2: KEY_YES,
        KEY_NOTE: TEXT_THE_SKILL_TOOL_WAS_VERIFIED_ON_V2_ONLY,
    },
    {
        KEY_FEATURE: TEXT_MCP_CONFIGURATION,
        KEY_V1: KEY_MCP,
        KEY_V2: TEXT_MCP_SERVERS,
        KEY_NOTE: TEXT_V2_REJECTS_THE_V1_SHAPE_SEE_AGENTS_MD_AND_ADR_001,
    },
    {
        KEY_FEATURE: TEXT_NATIVE_LSP_NAVIGATION,
        KEY_V1: KEY_EXPERIMENTAL,
        KEY_V2: KEY_NO,
        KEY_NOTE: TEXT_V1_REQUIRES_OPENCODE_EXPERIMENTAL_LSP_TOOL_V2_DOES_NOT_RUN_L,
    },
    {
        KEY_FEATURE: TEXT_CODE_MODE,
        KEY_V1: KEY_NO,
        KEY_V2: KEY_YES,
        KEY_NOTE: TEXT_CODE_MODE_GROUPS_MCP_TOOLS_AND_REDUCES_SCHEMA_OVERHEAD,
    },
    {
        KEY_FEATURE: TEXT_COMPACTION_CONTROLS,
        KEY_V1: TEXT_NOT_VERIFIED,
        KEY_V2: KEY_YES,
        KEY_NOTE: TEXT_VALIDATED_AGAINST_THE_V2_CONFIGURATION_LOADER,
    },
    {
        KEY_FEATURE: TEXT_TOOL_OUTPUT_LIMITS,
        KEY_V1: TEXT_NOT_VERIFIED,
        KEY_V2: KEY_YES,
        KEY_NOTE: TEXT_VALIDATED_AGAINST_THE_V2_CONFIGURATION_LOADER,
    },
    {
        KEY_FEATURE: TEXT_COST_STATISTICS_JSON,
        KEY_V1: TEXT_NOT_VERIFIED,
        KEY_V2: KEY_YES,
        KEY_NOTE: TEXT_OPENCODE_STATS_COST_JSON_IS_VERIFIED_ON_2_2_7,
    },
    {
        KEY_FEATURE: TEXT_SUBAGENT_DEPTH_CONTROL,
        KEY_V1: TEXT_NOT_VERIFIED,
        KEY_V2: KEY_YES,
        KEY_NOTE: TEXT_EXPERIMENTAL_SUBAGENT_DEPTH_IS_V2_NATIVE,
    },
)


def as_compatibility_dict() -> dict[str, Any]:
    return {
        KEY_TOOL: DEFAULT_ADAPTER,
        KEY_VERSIONS: [KEY_V1, KEY_V2],
        KEY_DISCLAIMER: DISCLAIMER,
        KEY_FEATURES: [dict(row) for row in MATRIX],
    }


def render_text() -> str:
    headers = (TEXT_FEATURE_LABEL, TEXT_V1, TEXT_V2, TEXT_NOTE)
    rows = [(row[KEY_FEATURE], row[KEY_V1], row[KEY_V2], row[KEY_NOTE]) for row in MATRIX]
    widths = [
        max(len(headers[0]), *(len(row[0]) for row in rows)),
        max(len(headers[1]), *(len(row[1]) for row in rows)),
        max(len(headers[2]), *(len(row[2]) for row in rows)),
    ]
    lines = [
        TEMPLATE_HEADER_ROW.format(headers[0], widths[0], headers[1], widths[1], headers[2], widths[2], headers[3]),
        TEXT_TEXT.format(TEXT_TEXT_2 * widths[0], TEXT_TEXT_2 * widths[1], TEXT_TEXT_2 * widths[2], TEXT_TEXT_2 * len(headers[3])),
    ]
    for feature, v1, v2, note in rows:
        lines.append(TEMPLATE_DATA_ROW.format(feature, widths[0], v1, widths[1], v2, widths[2], note))
    lines.extend([EMPTY_STRING, DISCLAIMER])
    return NEWLINE.join(lines)
