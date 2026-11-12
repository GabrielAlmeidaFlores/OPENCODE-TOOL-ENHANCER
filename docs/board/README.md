# Task Board

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** verified locally; opt-in

An optional Markdown task board for parallel work. It is never enabled by a default profile.

## Model

| Path | Purpose |
|---|---|
| `.ote/board/tasks/T-001.md` | One task per file; frontmatter is the state |
| `.ote/board/BOARD.md` | Generated table and WIP count |
| `.ote/worktrees/T-001` | Optional Git worktree; gitignored |

Statuses: `backlog`, `ready`, `in-progress`, `review`, `done`.

## Commands

```bash
ote task add "Add rate limiting" --verify "npm test -- rate-limit"
ote task add "Refactor auth" --worktree
ote task list
ote task move T-001 in-progress
ote task move T-001 review
ote task move T-001 done --approved
ote task status
ote task worktree T-001 --remove --yes
```

## Rules

- The WIP limit defaults to 3 (`[board] wip_limit` in `.ote/config.toml`).
- Moving to `done` requires `--approved`; the board never merges.
- Worktrees are created explicitly and use branch `task/<id>`.
- Removing a worktree requires `--remove --yes`; `--force` discards uncommitted changes and must be deliberate.
- The board never stages, commits, or pushes.

## Disable

Stop using the commands and delete `.ote/board`. Remove worktrees with `git worktree remove` or `ote task worktree <id> --remove --yes`.

## References

- `.ote/board/README.md` (source of truth in the project)
- `docs/cli/README.md`
- `docs/provenance/registry.yml`
