# Architecture Overview

## Layers

```text
┌──────────────────────────────────────────────────────────────┐
│ Human                                                        │
│ TUI, CLI, optional Telegram (Ralph RObot)                    │
└───────────────────────────┬──────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│ Orchestration: Ralph Orchestrator (primary)                  │
│ hats · events · completion promise · backpressure · memories │
└───────────────────────────┬──────────────────────────────────┘
                            │ opencode run --agent <role>
┌───────────────────────────▼──────────────────────────────────┐
│ OpenCode V2                                                  │
│ primary agent (coordinator) · subagents · permissions · commands    │
│ compaction · tool_output · skills · MCP clients              │
└───────┬───────────────────────────┬──────────────────────────┘
        │                           │
┌───────▼──────────────┐  ┌─────────▼───────────────────────────┐
│ Deterministic tools  │  │ Code intelligence                   │
│ tests, lint, tsc,    │  │ ripgrep · ast-grep · Serena MCP     │
│ formatters, git      │  │ CodeGraph MCP                       │
└──────────────────────┘  └─────────────────────────────────────┘
```

## Responsibilities

| Layer | Owns | Does not own |
| --- | --- | --- |
| Ralph | Task loop, gates, iteration limits, memories, worktrees | Tool permissions, model credentials |
| OpenCode | Agent prompts, permissions, tool execution, context compaction | Cross-session persistence |
| Deterministic tools | Correctness evidence | Reasoning about intent |
| Code intelligence | Retrieval precision | Deciding what to change |

## Request flow

1. A human or script invokes `ralph run` with a prompt or spec.
2. Ralph selects a hat and launches `opencode run --agent <role>`.
3. OpenCode loads the agent, project config, skills, and MCP servers.
4. The agent uses native tools, ripgrep, ast-grep, Serena, or CodeGraph as needed.
5. The agent runs deterministic checks (tests, lint, typecheck).
6. Ralph parses completion and gate outcomes. Incomplete work loops back.
7. On success Ralph emits the collection completion promise and runs its landing sequence. Ralph 2.10.1 commits during landing; see the Git safety section in the Ralph guide.

## Data and state

| State | Location | Owner |
| --- | --- | --- |
| Ralph memories/tasks/scratchpad | `.agent/` (or configured `.ralph/agent/`) | Ralph |
| Ralph specs | `.ralph/specs/` | Human/Ralph |
| OpenCode sessions | OpenCode data directory | OpenCode |
| CodeGraph index | `.codegraph/` | CodeGraph |
| Serena memories | Serena project config | Serena |
| Repository instructions | `AGENTS.md`, `.opencode/` | Human |

## Cost boundaries

- Ralph's memory injection has a token budget.
- OpenCode compaction retains a bounded tail.
- Tool output is capped by lines and bytes.
- MCP servers are exposed through Code Mode and permission filtering.
- Expensive checks run once per gate, not per iteration, where possible.

## Failure modes

| Failure | Detection | Response |
| --- | --- | --- |
| Model loops without progress | Iteration limit | Stop, report, preserve state |
| Tests fail | Non-zero exit | Gate blocks completion |
| Serena unavailable | MCP startup timeout | Fall back to ripgrep/ast-grep |
| CodeGraph stale | Auto-sync warning | Re-run `codegraph init` |
| Context overflow | Compaction event | Preserve decisions, drop raw output |
