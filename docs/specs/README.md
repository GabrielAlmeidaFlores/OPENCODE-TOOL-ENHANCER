# Spec-Driven Workflow

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally and in CI run 43277080347

Specs make a change reviewable before code is written and verifiable after. The workflow is adapted from `nerv`'s eight-phase SDD model (explore, propose, spec, design, tasks, apply, verify, archive), collapsed into four durable artifacts.

## Artifacts

```text
specs/<feature>/
├── requirements.md
├── design.md
├── tasks.md
└── evidence.md
```

| File | Owner | Contents |
|---|---|---|
| `requirements.md` | `planner` | Goals, testable criteria, non-goals |
| `design.md` | `architect` | Components, interfaces, decisions, risks |
| `tasks.md` | `planner` | Small tasks, each mapped to a criterion |
| `evidence.md` | `test-engineer` | Command or artifact proving each criterion |

## Commands

```bash
toolwright spec new "Add user authentication" \
  --criterion "A rejected password returns 401" \
  --criterion "A valid login returns a session"
toolwright spec list
toolwright spec plan user-authentication
toolwright spec verify user-authentication
```

`new` writes the four files. Without `--criterion`, the template contains a placeholder criterion.

`plan` fails until:

- at least one real criterion exists;
- at least one real task exists;
- every task names an existing criterion;
- every criterion has at least one task.

`verify` additionally requires evidence for every criterion and rejects evidence for unknown criteria.

## Format

```markdown
- [ ] AC-1: A rejected password returns 401
- [ ] T-1: Implement credential check (criterion: AC-1)
- AC-1: `npm test -- auth` passes
```

Checked boxes (`- [x]`) are accepted. Angle-bracket placeholders are ignored, so a fresh spec intentionally fails until filled in.

## Lifecycle

1. `toolwright spec new` — create the artifacts.
2. Fill requirements and design before implementation.
3. Break the design into tasks mapped to criteria.
4. Implement and run the verification commands.
5. Record the command and result in `evidence.md`.
6. `toolwright spec verify` must pass before the change is considered complete.

The coordinator delegates each step to the owning agent; the CLI supplies the deterministic checks.

## Limits

- The CLI verifies structure and mapping, not whether evidence is truthful or sufficient.
- Evidence commands are not executed by `spec verify`; `toolwright verify` runs the repository checks.
- One feature directory per change; rename the slug only before implementation starts.

## Design reference

The workflow follows `juanmanueldaza/nerv`'s SDD phase model (Apache-2.0), reduced to four artifacts to avoid a separate daemon or memory service. The implementation is original Python; see `docs/provenance/registry.yml` entry `memory-and-specs`.

## References

- `docs/memory/README.md`
- `specs/README.md`
- `docs/agents/roles.md`
