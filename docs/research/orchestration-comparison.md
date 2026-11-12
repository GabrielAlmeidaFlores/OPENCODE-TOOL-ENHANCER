# Orchestration Comparison

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally

Compared on 2026-11-11. Weights reflect this project's priorities: OpenCode fit, quality gates, and maintainability.

| Criterion | Ralph Orchestrator | OpenCode native | oh-my-opencode(-slim) | Claude Squad |
| --- | --- | --- | --- | --- |
| OpenCode compatibility | Community backend, plain text | Native | Plugin | External CLI/tmux |
| Multi-agent model | Hats + events | Primary + subagents | Built-in team | One agent per workspace |
| Model flexibility | Per-hat backend and args | Per-agent model | Plugin config | Per-session CLI |
| Custom agents | Hat YAML | Markdown/JSONC agents | Plugin-defined | Prompt only |
| Parallel execution | Worktree loops | Child sessions | Varies | Worktrees |
| Quality gates | Backpressure commands | Permissions only | Varies | None built in |
| Persistent memory | Memories + tasks | Session context | Varies | None |
| Human supervision | Telegram RObot | Interactive TUI | Interactive | tmux attach |
| Maturity | Active, 3.2k stars | Shipped | Third-party | Active |
| Install complexity | Medium (Rust/Node deps) | None | Low | Low |
| Token/cost controls | Iterations, runtime, memories budget | Compaction, tool limits | Varies | None |

## Selected: Ralph Orchestrator

Reasons:

1. It provides the missing loop, retry, completion, and backpressure semantics that OpenCode does not.
2. Hats can be routed to OpenCode agents with `backend.args`.
3. It keeps persistent state on disk, which supports resumable work and audit.
4. It does not require replacing OpenCode; OpenCode remains the model/tool runtime.

## Fallback: OpenCode native

Use native primary + subagents for:

- Single-file changes.
- Interactive exploration.
- Environments where installing Ralph is not permitted.

## Not selected

- **oh-my-opencode(-slim)**: promising, but adds a third-party plugin with its own agent model and upgrade cadence. Keep as a future evaluation.
- **Claude Squad**: solves parallel workspace management, not role orchestration or quality gates. Useful as an optional parallel runner.

## Decision rule

Use Ralph when a task has more than one verifiable step and needs gates. Use native OpenCode when the task is small, exploratory, or interactive. Never run both on the same working tree.
