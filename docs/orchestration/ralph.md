# Ralph Orchestration

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally

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

> **Auto-commit warning:** Ralph 2.10.1 commits its own changes during landing. Run every command in this section only inside a **separate disposable clone**, never in a repository where an automatic commit is unacceptable. A linked worktree is not sufficient: it shares `.git` with your repository.

```bash
# Inside a separate disposable clone
ralph run \
  -c configs/ralph/ralph.yml \
  -H configs/ralph/hats/code-assist.yml \
  -p "Implement <task with acceptance criteria>"
```

Ralph iterates until the collection emits its completion promise (`LOOP_COMPLETE`, `RESEARCH_COMPLETE`, `REVIEW_COMPLETE`, or `DEBUG_COMPLETE`) or a limit is reached.

## Run review, research, or debug

```bash
ralph run -c configs/ralph/ralph.yml -H configs/ralph/hats/review.yml   -p "Review the current diff"
ralph run -c configs/ralph/ralph.yml -H configs/ralph/hats/research.yml -p "Research <question>"
ralph run -c configs/ralph/ralph.yml -H configs/ralph/hats/debug.yml    -p "Debug <symptom>"
```

## How hats map to OpenCode agents

The collections are extracted from Ralph's official presets. Each hat adds only a `backend` block:

```yaml
hats:
  planner:
    backend:
      type: opencode
      args: ["--agent", "planner", "--auto"]
```

Ralph launches `opencode run --agent <role> "<prompt>"`. OpenCode applies that agent's prompt, permissions, steps, and tools.

| Collection | Hats | OpenCode agents |
| --- | --- | --- |
| `code-assist` | planner, builder, critic, finalizer | planner, backend-developer, code-reviewer, coordinator |
| `review` | reviewer, analyzer, closer | code-reviewer, security-reviewer, coordinator |
| `research` | researcher, synthesizer | researcher, coordinator |
| `debug` | investigator, tester, fixer, verifier | researcher, test-engineer, backend-developer, test-engineer |

For frontend-only work, change the `builder` backend to `frontend-developer` in a local copy and record the modification in the provenance registry.

## Event flow

`code-assist` (official preset):

```text
build.start
  -> tasks.ready      (planner)
  -> review.ready     (builder)        review.rejected / finalization.failed -> builder
  -> review.passed    (critic)         review.rejected -> builder
  -> queue.advance    (finalizer)      next wave -> planner
  -> LOOP_COMPLETE    (finalizer)
```

- `review`: `review.start -> review.section -> analysis.complete -> review.followup / REVIEW_COMPLETE`
- `research`: `research.start -> research.finding -> research.followup / RESEARCH_COMPLETE`
- `debug`: `debug.start -> hypothesis.test -> hypothesis.confirmed / fix.propose -> fix.applied -> fix.verified / DEBUG_COMPLETE`

Each collection sets its own `starting_event` and `required_events`; `configs/ralph/ralph.yml` provides the shared loop, backend, memory, and task settings.

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

The `code-assist` collection sets `event_loop.required_events: ["review.passed"]`. Completion is gated on an approved review. The `critic` can reject with `review.rejected`; the `finalizer` checks acceptance criteria before emitting `LOOP_COMPLETE`.

For deterministic gates, record the exact commands in `AGENTS.md`. Do not gate on prose.

## Verified workflows

- `research` completed in **2 iterations** with `RESEARCH_COMPLETE` in the test project.
- `code-assist` is a longer multi-wave workflow. In the same test project it required more than 8 iterations for a small change; raise `--max-iterations` for real features, or use `research`/`review` for smaller scopes.

## Git safety

Ralph Orchestrator 2.10.1 auto-commits during its landing sequence (`LandingConfig::default().auto_commit = true`) and exposes no configuration switch. This violates this repository's no-auto-commit rule.

Do not run Ralph directly in a repository that must remain uncommitted. Use the isolated runner:

```bash
./scripts/maintenance/run-ralph-isolated.sh -- \
  -c configs/ralph/ralph.yml \
  -H configs/ralph/hats/research.yml \
  -p "Research <question>"
```

The runner copies the working tree to a separate clone, creates a baseline commit there, runs Ralph, exports the result to `.ralph-isolated/<timestamp>.patch`, and leaves the clone for inspection. Add `--apply` to apply the patch to the current checkout unstaged; add `--cleanup` to remove the clone.

Do not use a linked worktree as a substitute; it shares `.git` and writes commits and refs into the same repository. Use the native OpenCode agents for tasks that must not create commits.

`features.auto_merge` is already `false`, but it does not disable landing auto-commit.

## Memory and tasks

- `memories.budget: 2000` bounds injected context.
- `tasks.enabled: true` persists runtime work tracking.
- Scratchpads live under `.ralph/agent/` and are excluded from Git.

## Parallelism

`features.parallel` is **false** by default. This is Ralph's parallel worktree feature, not a substitute for the separate clone required above. Enable it only when tasks touch disjoint files. CodeGraph permits one MCP writer per project, so two agents must not both run `codegraph serve --mcp` against the same tree.

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
| Loop never completes | The collection did not emit its completion promise; inspect `.ralph/agent/scratchpad.md` |
| Tests pass in Ralph but not locally | The builder or critic used a different command or working directory |
| MCP startup timeout | Raise `adapters.opencode.timeout` and the MCP `startup` timeout |
