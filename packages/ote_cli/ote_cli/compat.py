"""
OpenCode V1 and V2 compatibility matrix.

Public API: :data:`MATRIX`, :func:`as_dict`, and :func:`render_text`.

The matrix records only behaviour documented in ``docs/decisions/ADR-001`` or
verified in this repository. Cells that were not verified are marked as such.

Side effects: none.
"""
from __future__ import annotations

from typing import Any

DISCLAIMER = "Compatibility matrix only; it records supported features, not performance or benchmark results."

MATRIX: tuple[dict[str, str], ...] = (
    {
        "feature": "Agent definitions",
        "v1": "yes",
        "v2": "yes",
        "note": "Markdown agents with frontmatter are read by both versions.",
    },
    {
        "feature": "Slash commands",
        "v1": "yes",
        "v2": "yes",
        "note": "Command files and agent targets are supported by both.",
    },
    {
        "feature": "Skills",
        "v1": "not verified",
        "v2": "yes",
        "note": "The skill tool was verified on V2 only.",
    },
    {
        "feature": "MCP configuration",
        "v1": "mcp",
        "v2": "mcp.servers",
        "note": "V2 rejects the V1 shape; see AGENTS.md and ADR-001.",
    },
    {
        "feature": "Native LSP navigation",
        "v1": "experimental",
        "v2": "no",
        "note": "V1 requires OPENCODE_EXPERIMENTAL_LSP_TOOL; V2 does not run language servers.",
    },
    {
        "feature": "Code Mode",
        "v1": "no",
        "v2": "yes",
        "note": "Code Mode groups MCP tools and reduces schema overhead.",
    },
    {
        "feature": "Compaction controls",
        "v1": "not verified",
        "v2": "yes",
        "note": "Validated against the V2 configuration loader.",
    },
    {
        "feature": "Tool output limits",
        "v1": "not verified",
        "v2": "yes",
        "note": "Validated against the V2 configuration loader.",
    },
    {
        "feature": "Cost statistics JSON",
        "v1": "not verified",
        "v2": "yes",
        "note": "opencode stats --cost --json is verified on 2.2.7.",
    },
    {
        "feature": "Subagent depth control",
        "v1": "not verified",
        "v2": "yes",
        "note": "experimental.subagent_depth is V2-native.",
    },
)


def as_dict() -> dict[str, Any]:
    """
    Return the matrix as a JSON-serializable document.
    """
    return {
        "tool": "opencode",
        "versions": ["v1", "v2"],
        "disclaimer": DISCLAIMER,
        "features": [dict(row) for row in MATRIX],
    }


def render_text() -> str:
    """
    Render the matrix as a fixed-width table for terminal output.
    """
    headers = ("Feature", "V1", "V2", "Note")
    rows = [(row["feature"], row["v1"], row["v2"], row["note"]) for row in MATRIX]
    widths = [
        max(len(headers[0]), *(len(row[0]) for row in rows)),
        max(len(headers[1]), *(len(row[1]) for row in rows)),
        max(len(headers[2]), *(len(row[2]) for row in rows)),
    ]
    lines = [
        f"{headers[0]:<{widths[0]}}  {headers[1]:<{widths[1]}}  {headers[2]:<{widths[2]}}  {headers[3]}",
        f"{'-' * widths[0]}  {'-' * widths[1]}  {'-' * widths[2]}  {'-' * len(headers[3])}",
    ]
    for feature, v1, v2, note in rows:
        lines.append(f"{feature:<{widths[0]}}  {v1:<{widths[1]}}  {v2:<{widths[2]}}  {note}")
    lines.extend(["", DISCLAIMER])
    return "\n".join(lines)
