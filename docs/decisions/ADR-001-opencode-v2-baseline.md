# ADR-001: Target OpenCode V2 as the validated baseline

- Status: Accepted
- Date: 2026-11-11

## Context

At the start of the project the local machine had OpenCode **1.19.5** installed, while the published npm `latest` was **2.2.7**. The public documentation is split: `/docs/config` and `/docs/agents` describe V2, while `/docs/lsp` is explicitly labelled V1.

The project requires code intelligence. V1 exposes an experimental LSP tool (`OPENCODE_EXPERIMENTAL_LSP_TOOL=true`) with `goToDefinition`, `findReferences`, `documentSymbol`, `workspaceSymbol`, `goToImplementation`, and call-hierarchy operations. The V2 migration guide states:

> V2 accepts and preserves `lsp` configuration, but it does not run language servers, expose LSP tools, or produce LSP diagnostics.

## Decision

Target **OpenCode V2 (2.2.7)** as the validated baseline and replace native LSP with Serena over MCP for symbol-level navigation.

V1 remains documented only as a migration reference. V2 reads supported V1 configuration, so users are not forced to rewrite existing files immediately.

## Consequences

- Native LSP diagnostics and LSP navigation are unavailable. Serena, ast-grep, and project lint/typecheck commands cover the gap.
- Configuration uses V2-native keys: `agents`, `permissions`, `mcp.servers`, `commands`, `skills`, `compaction`, `tool_output`.
- V2 Code Mode is available for MCP servers and reduces tool-description overhead, which matters for the maximal toolset.
- `opencode stats --cost --json` provides cost and token telemetry for the benchmark harness.
- Documentation must not present V1-only examples as current.

## Verification

Performed non-destructively against a standalone V2 binary in a temporary directory:

```text
opencode v2.2.7
run flags include --agent, --model, --format {default,json}
stats flags include --cost, --project, --json
mcp subcommands: list, add, auth, logout
```

## References

- https://opencode.ai/docs/migrate-v1
- https://opencode.ai/docs/config
- https://opencode.ai/docs/agents
- https://opencode.ai/config.json
