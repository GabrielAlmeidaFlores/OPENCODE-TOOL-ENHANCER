# Ralph Orchestration

Ralph Orchestrator is the primary orchestration framework. It owns the loop, retries, completion, gates, and persistent state. OpenCode remains the model and tool runtime.

- Repository: https://github.com/mikeyobrien/ralph-orchestrator
- Version used: 2.10.1
- License: MIT

## Install

```bash
npm install -g @ralph-orchestrator/ralph-cli
ralph --version
```

Node >= 18 is required. Rust is only needed for the optional web dashboard (`ralph web`), not for `ralph run`.

## Initialize

```bash
ralph init --backend opencode
```

This creates a `ralph.yml`. The repository's configuration is in `configs/ralph/`; copy or reference it rather than overwriting it blindly.

## Run the implementation workflow

```bash
ralph run \
  -c configs/ralph/ralph.yml \
  -H configs/ralph/hats/code-assist.yml \
  -p "Implement <task with acceptance criteria>"
```

Ralph iterates until the finalizer emits `LOOP_COMPLETE` or a limit is reached.

## Run review, research, or debug

```bash
ralph run -c configs/ralph/ralph.yml -H configs/ralph/hats/review.yml   -p "Review the current diff"
ralph run -c configs/ralph/ralph.yml -H configs/ralph/hats/research.yml -p "Research <question>"
ralph run -c configs/ralph/ralph.yml -H configs/ralph/hats/debug.yml    -p "Debug <symptom>"
```

## How hats map to OpenCode agents

Each hat sets `backend.args`:

```yaml
hats:
  planner:
    backend:
      type: opencode
      args: ["--agent", "planner"]
```

Ralph launches `opencode run --agent <role> "<prompt>"`. OpenCode applies that agent's prompt, permissions, steps, and tools.

## Event flow

```text
work.start
  -> plan.ready        (planner)
  -> build.ready       (builder)       tests.failed / review.rejected -> builder
  -> tests.passed      (validator)     tests.failed -> builder
  -> review.approved   (reviewer)      review.rejected -> builder
  -> LOOP_COMPLETE     (finalizer)
```

## Headless permissions

Ralph runs OpenCode non-interactively, so every hat passes `--auto`:

```yaml
args: ["--agent", "planner", "--auto"]
```

For prompts over 7000 characters Ralph writes the prompt to a temporary file and asks the agent to read it. The OpenCode config allows transient temp directories for this purpose:

```jsonc
{ "action": "external_directory", "resource": "/var/folders/**", "effect": "allow" },
{ "action": "external_directory", "resource": "/private/var/folders/**", "effect": "allow" },
{ "action": "external_directory", "resource": "/tmp/**", "effect": "allow" }
```

This is narrow: it does not allow arbitrary external paths. Destructive commands (`sudo`, `rm -rf`, force-push) remain hard-denied even under `--auto`.

## Quality gates

The `code-assist` collection sets `event_loop.required_events: ["review.approved"]`, so completion is gated on review. Other collections are not gated by that event.

Gates are enforced by the `validator` and `reviewer` hats:

- The validator executes tests, lint, and typecheck itself; it does not trust the builder's claim.
- A non-zero exit produces `tests.failed` and returns work to the builder.
- The reviewer can reject on blocker or major findings.
- The finalizer checks each acceptance criterion before completion.

For deterministic gates, record the exact commands in `AGENTS.md`. Do not gate on prose.

## Memory and tasks

- `memories.budget: 2000` bounds injected context.
- `tasks.enabled: true` persists runtime work tracking.
- Scratchpads live under `.ralph/agent/` and are excluded from Git.

## Parallelism

`features.parallel` is **false** by default. Enable worktree loops only when tasks touch disjoint files. CodeGraph permits one MCP writer per project, so two agents must not both run `codegraph serve --mcp` against the same tree.

## Known limitations

1. The OpenCode backend is community support and uses plain-text output. There is no structured event stream.
2. Per-hat `args` are forwarded verbatim; an unsupported OpenCode flag will fail the run.
3. The published cost-management page contains stale commands (`python ralph_orchestrator.py --max-cost`). Current `ralph run` limits are `--max-iterations`, `--completion-promise`, and `--idle-timeout`; configure runtime in `event_loop`.
4. `ralph web` is alpha.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `No AI agents detected` | `opencode --version`; ensure it is on `PATH` |
| Hangs on first iteration | Run `opencode run --agent planner "test"` directly |
| Loop never completes | The finalizer did not emit `LOOP_COMPLETE`; inspect `.ralph/agent/scratchpad.md` |
| Tests pass in Ralph but not locally | The validator used a different command or working directory |
| MCP startup timeout | Raise `adapters.opencode.timeout` and the MCP `startup` timeout |
