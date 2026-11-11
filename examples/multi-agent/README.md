# Multi-Agent Example

A complete feature workflow using Ralph hats and OpenCode agents.

## Goal

Add request validation to `examples/typescript`, with tests and a review.

## Run (isolated)

> **Auto-commit warning:** Ralph 2.10.1 commits its own changes during landing. Do not run it in this repository. Use a separate disposable clone; a linked worktree is not sufficient because it shares `.git`.

```bash
# From the main checkout, capture any uncommitted work as a patch.
git diff > /tmp/ote-work.patch

# Create a separate clone and start from the same state.
git clone . /tmp/ote-ralph
cd /tmp/ote-ralph
git apply /tmp/ote-work.patch

# Record the starting point as a deliberate baseline commit in the disposable
# clone, so Ralph's landing commit contains only its own changes.
git add -A && git commit -m "baseline for isolated Ralph run"

# Run Ralph only here. It will create its own commit in this clone.
ralph run \
  -c configs/ralph/ralph.yml \
  -H configs/ralph/hats/code-assist.yml \
  -p "In examples/typescript, require age to be a non-negative integer in validateCreateUser, add tests, and run npm test"
```

After the run, review the clone and export the change without touching the main checkout:

```bash
git -C /tmp/ote-ralph log --oneline -3
git -C /tmp/ote-ralph format-patch -1 --stdout > /tmp/ralph-change.patch

cd /path/to/OPENCODE-TOOL-ENHANCER
git apply /tmp/ralph-change.patch   # applies unstaged
```

`git diff` does not include untracked files. Add them to the patch manually if your task creates new files.

## Expected event flow

The `code-assist` collection is Ralph's official preset:

```text
build.start -> tasks.ready -> review.ready -> review.passed -> queue.advance -> LOOP_COMPLETE
```

It is a multi-wave workflow. For a first run, use `--max-iterations 20` or try the shorter `research` collection.

## Inspect

- `.ralph/agent/scratchpad.md` — current reasoning and progress
- `.ralph/agent/memories.md` — durable learnings
- `.ralph/agent/tasks.jsonl` — task records

## If it fails

| Point | Action |
| --- | --- |
| No `tasks.ready` | Check that the planner created a runtime task and emitted the event |
| `review.ready` loops | Inspect the builder output; it may be blocked |
| `review.rejected` | Read the finding, fix, and re-run |
| `build.blocked` | Read the blocker payload and resolve the missing input |
| Never completes | Verify the finalizer can see the acceptance criteria and that `review.passed` was emitted |

## Variant: native OpenCode

For a smaller task, skip Ralph:

```bash
opencode run --agent coordinator "Add the age validation and run npm test in examples/typescript"
```
