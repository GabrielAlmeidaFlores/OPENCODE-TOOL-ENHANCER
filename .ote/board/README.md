# Task Board

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** verified locally

Optional Markdown task board for parallel work. It is not enabled by any default profile; use `ote task` explicitly.

## State

```text
.ote/board/
├── BOARD.md          generated table
└── tasks/T-001.md    one file per task
.ote/worktrees/T-001  optional Git worktree (gitignored)
```

`BOARD.md` is generated from the task files. The frontmatter is the state; prose below it is free form.

## Commands

```bash
ote task add "Add rate limiting" --verify "npm test -- rate-limit"
ote task add "Refactor auth" --worktree
ote task list
ote task list --status in-progress
ote task move T-001 in-progress
ote task move T-001 done --approved
ote task status
ote task worktree T-002 --remove --yes
```

## Rules

- Statuses: `backlog`, `ready`, `in-progress`, `review`, `done`.
- The WIP limit defaults to 3 and is configurable in `.ote/config.toml` under `[board]`.
- Moving to `done` requires `--approved`; the board never merges.
- Worktrees live under `.ote/worktrees/` and use branch `task/<id>`.
- The board never stages, commits, or pushes.
- Removing a worktree requires `--remove`; add `--force` only after reviewing uncommitted changes.

## Configuration

```toml
[board]
wip_limit = 3
```

## Enabling and disabling

The board is available whenever `ote` is installed; it creates its directory on first use. Delete `.ote/board` to remove the state. Worktrees must be removed with `git worktree remove` or `ote task worktree <id> --remove --yes`.
