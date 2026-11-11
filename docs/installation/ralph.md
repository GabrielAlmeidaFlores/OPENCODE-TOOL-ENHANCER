# Install Ralph Orchestrator

## Prerequisites

- Node >= 18
- OpenCode V2 installed and authenticated
- Optional: Rust toolchain only for `ralph web`

## Install

```bash
npm install -g @ralph-orchestrator/ralph-cli
ralph --version
```

Expected: `2.10.x`.

## Initialize

```bash
ralph init --backend opencode
```

This writes a `ralph.yml` in the current directory. The repository's configuration is under `configs/ralph/`; use it directly rather than accepting defaults.

## Verify the backend

```bash
opencode run --agent coordinator "Reply with OK"
ralph preflight --format human
```

`ralph preflight` checks config, hooks, backend, git, paths, tools, and specs. Treat warnings as actionable, not decorative.

## First run

```bash
ralph run \
  -c configs/ralph/ralph.yml \
  -H configs/ralph/hats/code-assist.yml \
  -p "Add input validation to the example TypeScript endpoint and verify with tests"
```

## Configuration options that matter

| Option | Value | Why |
| --- | --- | --- |
| `cli.backend` | `opencode` | Use OpenCode as the runtime |
| `adapters.opencode.timeout` | `900` | MCP and language-server startup |
| `event_loop.max_iterations` | `40` | Cost ceiling |
| `memories.budget` | `2000` | Bound injected context |
| `features.parallel` | `false` | Avoid index and file conflicts |

## Common problems

| Symptom | Fix |
| --- | --- |
| Backend not found | `which opencode`; it must be on `PATH` |
| Auth failure | Run OpenCode directly once |
| Hangs on first iteration | Raise `adapters.opencode.timeout` |
| Never completes | Check the finalizer hat emits `LOOP_COMPLETE` |
| Gate passes incorrectly | The validator must run commands itself |

## Uninstall

```bash
npm uninstall -g @ralph-orchestrator/ralph-cli
```

State under `.ralph/` is project-local; remove it separately if desired.

## References

- https://github.com/mikeyobrien/ralph-orchestrator
- https://mikeyobrien.github.io/ralph-orchestrator/guide/backends/
- https://mikeyobrien.github.io/ralph-orchestrator/guide/configuration/
