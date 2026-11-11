# ADR-002: Ralph Orchestrator as the primary orchestration framework

- Status: Accepted
- Date: 2026-11-11

## Context

The project needs structured multi-agent execution with quality gates, persistence, and parallel execution. Candidate approaches were:

1. **Ralph Orchestrator** (`mikeyobrien/ralph-orchestrator`, MIT, v2.10.1)
2. **OpenCode native** primary agent + subagents + commands
3. **oh-my-opencode(-slim)** plugin
4. **Claude Squad** (tmux + git worktrees)

Ralph provides hat/event orchestration, backpressure gates, persistent memories and tasks, worktree loops, and Telegram human-in-the-loop. Its OpenCode backend is documented as **community** support: the adapter runs `opencode run "<prompt>"` and parses plain text, with no JSON streaming (`crates/ralph-adapters/src/cli_backend.rs`).

Phase 0 verified that V2 still provides `opencode run` with a positional prompt and `--agent`/`--model`, and that Ralph hats accept `backend_args` (alias `args`), so per-hat agent routing is possible.

## Decision

Use **Ralph Orchestrator as the primary orchestration framework**, with the **OpenCode-native agent stack as the fallback** for short or interactive tasks.

Ralph hats map to OpenCode agents through per-hat `args`, for example:

```yaml
hats:
  planner:
    backend:
      type: opencode
      args: ["--agent", "planner"]
```

## Consequences

- Ralph owns looping, retries, completion promises, gates, and persistent state.
- OpenCode owns model access, tools, permissions, and context management.
- The integration depends on Ralph's plain-text parsing; gate output must be machine-checkable (exit codes, not prose).
- Ralph documentation contains stale cost commands (`python ralph_orchestrator.py --max-cost`). This repository does not reproduce them; current `ralph run` flags are used.
- Two orchestration systems are not run simultaneously for the same task.

## Alternatives retained

- Native OpenCode orchestration is documented as the zero-infrastructure baseline.
- oh-my-opencode and Claude Squad remain candidates for future evaluation; neither is a default.

## References

- https://github.com/mikeyobrien/ralph-orchestrator
- https://mikeyobrien.github.io/ralph-orchestrator/guide/backends/
- https://mikeyobrien.github.io/ralph-orchestrator/advanced/architecture/
