# Phase 1 Research Report

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally

- Date: 2026-11-11
- Scope: OpenCode capabilities, Ralph Orchestrator, orchestration alternatives, code-intelligence tools, cost evidence.
- Method: official documentation, release metadata, repository source reading, and non-destructive CLI verification.

## 1. Environment observed

| Item | Value |
| --- | --- |
| Installed OpenCode | 1.19.5 (V1 line) |
| npm `latest` | 2.2.7 |
| Node | 24.18.0 |
| Available | `python3`, `git`, `rg`, `ctags` |
| Missing | `ast-grep`, `serena`, `codegraph`, `ralph` |
| Existing global config | V1 schema (`mcp.<name>`, `enabled`) |

## 2. OpenCode version findings

The documentation set is in transition. V2 documentation describes `agents`, `permissions`, `mcp.servers`, `system`, `steps`, `skills`, and `commands`. V1 documentation describes `agent`, `permission`, `mcp.<name>`, `prompt`, `maxSteps`, `tools`, and a file-based `agents/` layout.

The decisive difference for this project is LSP:

- V1: built-in LSP servers, diagnostics feedback, and an experimental LSP navigation tool.
- V2: accepts `lsp` configuration but does not run language servers or expose LSP tools.

Decision: target V2 and use Serena for semantic navigation. See [ADR-001](../decisions/ADR-001-opencode-v2-baseline.md).

Verified against a standalone 2.2.7 binary:

```text
opencode v2.2.7
opencode run [flags] [<message...>]
  --agent string
  --model, -m string        (provider/model#variant)
  --format {default,json}
opencode stats
  --cost  --json  --project  --days  --tools  --models
opencode mcp {list,add,auth,logout}
```

The configuration schema at `https://opencode.ai/config.json` accepts both V1 and V2 keys, so V2 can load existing V1 files. New examples in this repository use V2 keys.

## 3. Ralph Orchestrator findings

- Version 2.10.1, MIT, Rust workspace with `ralph-proto`, `ralph-core`, `ralph-adapters`, `ralph-tui`, `ralph-cli`, `ralph-e2e`, `ralph-bench`.
- Strengths: hat/event routing, completion promise (`LOOP_COMPLETE`), backpressure gates, persistent memories and tasks, worktree loops, Telegram human-in-the-loop, presets for code-assist, debug, review, spec-driven, PR review, and wave review.
- OpenCode is a **community** backend. The adapter runs `opencode run "<prompt>"` with plain-text output; there is no JSON stream. Auto-detection places OpenCode eighth.
- Hats expose `backend_args` with the shorthand `args`, so per-hat agent routing is possible.
- The cost-management documentation still shows `python ralph_orchestrator.py --max-cost/--max-tokens`. These are not current `ralph run` flags. Treat that page as stale.

Classification: independently verified by source reading and documentation, not by running Ralph yet. End-to-end execution is a Phase 3 acceptance test.

## 4. Orchestration comparison

| Framework | OpenCode fit | Multi-agent | Parallel | Gates/memory | Maturity | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| Ralph Orchestrator | Backend exists, plain text | Hats + events | Worktrees | Strong | Active, 3.2k stars | Primary |
| OpenCode native | Native | Primary + subagents | Child sessions | Permissions only | Shipped | Fallback/baseline |
| oh-my-opencode(-slim) | Plugin | Built-in team | Plugin-dependent | Varies | Third-party | Evaluate only |
| Claude Squad | CLI-agnostic tmux | Workspace per task | Worktrees | None | Active | Not a role orchestrator |

## 5. Code-intelligence findings

### ast-grep

- Version 0.51.1 installed; 0.51.2 was released 2026-11-11. MIT.
- Tree-sitter structural search and rewrite; YAML rules; no MCP required.
- Best for deterministic "find this syntax shape" queries and lint-style rules.
- Not a symbol resolver; cannot replace semantic navigation.

### Serena

- Version 2.1.0, released 2026-10-19; GPL-3.0-or-later (SolidLSP MIT).
- MCP server; 40+ languages through LSP backends; symbol retrieval, references, edits, and rename.
- Recommended OpenCode-like context: `--context ide` to reduce duplicated basic tools.
- Costs: language-server startup time, memory, and MCP tool schema. Requires tool trimming.

### CodeGraph

- `colbymchenry/codegraph`, 77k stars, active, MIT.
- Local graph in SQLite, Rust kernel, tree-sitter, auto-sync, OpenCode support.
- MCP command: `codegraph serve --mcp`; per-project setup: `codegraph init`.
- Costs: indexing time and disk; one active writer per project.

### ripgrep

- Fast text search; already installed. Native OpenCode search uses ripgrep-style behavior.

### Optional tools

- Repomix: packs a repository; useful for whole-repo analysis, counterproductive as a default for targeted edits.
- jCodeMunch: symbol retrieval over MCP; dual-use license, commercial use requires payment; vendor benchmark claims 96.2% fewer tokens per lookup, not independently reproduced here.
- Universal Ctags: cheap symbol index; useful for editors/scripts, limited semantic depth.
- Graphify: the URL `github.com/graphify` is not the maintained code-graph project; the active project is `Graphify-Labs/graphify`. It is a skill/cloud product and remains optional.
- Aider repository map: not a standalone OpenCode integration; not adopted.

## 6. Cost evidence

| Claim | Source | Classification |
| --- | --- | --- |
| jCodeMunch reduces tokens 96.2% per lookup | Vendor benchmark in its README | Vendor claim, not independently verified |
| Graphify cuts agent token spend by 80% | Marketing copy | Vendor claim, not independently verified |
| Ralph optimizes a "smart zone" at 40-60% context | Project documentation | Design guidance, not a measured result |
| V2 Code Mode reduces tool-description overhead | OpenCode documentation | Product design; effect size unmeasured here |

No savings figure is published by this repository. See [ADR-004](../decisions/ADR-004-benchmark-scope.md).

## 7. Risks

1. Ralph's plain-text OpenCode integration may be brittle if output formats change.
2. V2 removes LSP; Serena must be healthy or symbol-level navigation is lost.
3. CodeGraph and Serena both index the workspace; running both on very large repositories increases startup and memory cost.
4. MCP tool schemas can dominate context if Code Mode or permission filtering is misconfigured.
5. Third-party licenses (GPL-3.0, commercial dual-use) affect redistribution and commercial use.

## 8. References

- https://opencode.ai/docs/
- https://opencode.ai/docs/config
- https://opencode.ai/docs/agents
- https://opencode.ai/docs/mcp-servers
- https://opencode.ai/docs/migrate-v1
- https://opencode.ai/config.json
- https://github.com/mikeyobrien/ralph-orchestrator
- https://mikeyobrien.github.io/ralph-orchestrator/guide/backends/
- https://mikeyobrien.github.io/ralph-orchestrator/advanced/architecture/
- https://github.com/ast-grep/ast-grep
- https://github.com/oraios/serena
- https://github.com/colbymchenry/codegraph
- https://github.com/yamadashy/repomix
- https://github.com/jgravelle/jcodemunch-mcp
- https://github.com/universal-ctags/ctags
- https://github.com/Graphify-Labs/graphify
