# Specs

Spec-driven development artifacts managed by `toolwright spec`. Each feature gets a directory with four files:

| File | Purpose |
|---|---|
| `requirements.md` | Goals, testable acceptance criteria, non-goals |
| `design.md` | Components, interfaces, decisions, risks |
| `tasks.md` | Small tasks, each mapped to a criterion |
| `evidence.md` | Command or artifact proving each criterion |

## Workflow

```bash
toolwright spec new "Add user authentication" --criterion "A rejected password returns 401" --criterion "A valid login returns a session"
toolwright spec plan user-authentication
toolwright spec list
toolwright spec verify user-authentication
```

`plan` fails until every criterion has at least one task and every task names a valid criterion. `verify` additionally requires evidence for every criterion.

## Format

Criteria and tasks use checkbox lines:

```markdown
- [ ] AC-1: A rejected password returns 401
- [ ] T-1: Implement credential check (criterion: AC-1)
- AC-1: `npm test -- auth` passes
```

Checked boxes (`- [x]`) are accepted. Angle-bracket placeholders from the template are ignored, so a freshly created spec fails verification until it is filled in.

## Ownership

| Agent | Responsibility |
|---|---|
| `planner` | Requirements and tasks |
| `architect` | Design and decisions |
| `test-engineer` | Evidence commands and results |
| `code-reviewer` | Checks that evidence matches the criterion |

See [`docs/specs/README.md`](../docs/specs/README.md) for the full workflow.
