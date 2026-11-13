# Task Board

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** verified locally

Optional Markdown task board for parallel work. It is not enabled by any default profile; use `toolwright task` explicitly.

## State

```text
.toolwright/board/
├── BOARD.md          generated table
└── tasks/T-001.md    one file per task
.toolwright/worktrees/T-001  optional Git worktree (gitignored)
```

`BOARD.md` is generated from the task files. The frontmatter is the state; prose below it is free form.

## Commands

```bash
toolwright task add "Add rate limiting" --verify "npm test -- rate-limit"
toolwright task add "Refactor auth" --worktree
toolwright task list
toolwright task list --status in-progress
toolwright task move T-001 in-progress
toolwright task move T-001 done --approved
toolwright task status
toolwright task worktree T-002 --remove --yes
```

## Rules

- Statuses: `backlog`, `ready`, `in-progress`, `review`, `done`.
- The WIP limit defaults to 3 and is configurable in [`.toolwright/config.toml`](../config.toml) under `[board]`.
- Moving to `done` requires `--approved`; the board never merges.
- Worktrees live under `.toolwright/worktrees/` and use branch `task/<id>`.
- The board never stages, commits, or pushes.
- Removing a worktree requires `--remove`; add `--force` only after reviewing uncommitted changes.

## Configuration

```toml
[board]
wip_limit = 3
```

## Enabling and disabling

The board is available whenever `toolwright` is installed; it creates its directory on first use. Delete `.toolwright/board` to remove the state. Worktrees must be removed with `git worktree remove` or `toolwright task worktree <id> --remove --yes`.
