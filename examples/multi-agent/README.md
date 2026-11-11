# Multi-Agent Example

A complete feature workflow using Ralph hats and OpenCode agents.

## Goal

Add request validation to `examples/typescript`, with tests and a review.

## Run

```bash
# From the repository root, with Ralph installed
ralph run \
  -c configs/ralph/ralph.yml \
  -H configs/ralph/hats/code-assist.yml \
  -p "In examples/typescript, require age to be a non-negative integer in validateCreateUser, add tests, and run npm test"
```

## Expected event flow

```text
work.start -> plan.ready -> build.ready -> tests.passed -> review.approved -> LOOP_COMPLETE
```

## Inspect

- `.ralph/agent/scratchpad.md` — current reasoning and progress
- `.ralph/agent/memories.md` — durable learnings
- `.ralph/agent/tasks.jsonl` — task records

## If it fails

| Point | Action |
| --- | --- |
| No `plan.ready` | Check the planner emits `<event topic="plan.ready">...</event>` |
| `tests.failed` repeatedly | Run `npm test` manually in the example |
| `review.rejected` | Read the finding, fix, and re-run |
| Never completes | Verify the finalizer can see the acceptance criteria |

## Variant: native OpenCode

For a smaller task, skip Ralph:

```bash
opencode run --agent coordinator "Add the age validation and run npm test in examples/typescript"
```
