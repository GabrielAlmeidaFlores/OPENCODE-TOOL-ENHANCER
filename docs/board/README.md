# Task Board

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** verified locally; opt-in

An optional Markdown task board for parallel work. It is never enabled by a default profile.

## Model

| Path | Purpose |
|---|---|
| `.toolwright/board/tasks/T-001.md` | One task per file; frontmatter is the state |
| [`.toolwright/board/BOARD.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/.toolwright/board/BOARD.md) | Generated table and WIP count |
| `.toolwright/worktrees/T-001` | Optional Git worktree; gitignored |

Statuses: `backlog`, `ready`, `in-progress`, `review`, `done`.

## Commands

```bash
toolwright task add "Add rate limiting" --verify "npm test -- rate-limit"
toolwright task add "Refactor auth" --worktree
toolwright task list
toolwright task move T-001 in-progress
toolwright task move T-001 review
toolwright task move T-001 done --approved
toolwright task status
toolwright task worktree T-001 --remove --yes
```

## Rules

- The WIP limit defaults to 3 (`[board] wip_limit` in [`.toolwright/config.toml`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/.toolwright/config.toml)).
- Moving to `done` requires `--approved`; the board never merges.
- Worktrees are created explicitly and use branch `task/<id>`.
- Removing a worktree requires `--remove --yes`; `--force` discards uncommitted changes and must be deliberate.
- The board never stages, commits, or pushes.

## Disable

Stop using the commands and delete `.toolwright/board`. Remove worktrees with `git worktree remove` or `toolwright task worktree <id> --remove --yes`.

## References

- [`.toolwright/board/README.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/.toolwright/board/README.md) (source of truth in the project)
- [`docs/cli/README.md`](../cli/README.md)
- [`docs/provenance/registry.yml`](../provenance/registry.yml)
