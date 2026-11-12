# Deterministic Evaluations

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally; CI runs `ote eval`

`ote eval` runs repository invariants that must hold without a model. It is a regression net for the profile itself, not a model benchmark.

## Cases

Cases live in `tests/evals/cases.json`:

| Case | What it proves |
|---|---|
| `profiles` | Every manifest loads and validates |
| `catalog` | The generated catalog matches its schema, counts, and local paths |
| `governance` | Every agent contract satisfies its role rules |
| `validator` | The repository validator exits zero |

## Commands

```bash
ote eval
ote eval --only profiles
ote eval --json
```

Exit code 0 means every selected case passed; 1 means at least one failed; 2 means a configuration error.

## Adding a case

1. Implement the check in `packages/ote_cli/ote_cli/eval.py`.
2. Add the case id and description to `tests/evals/cases.json`.
3. Add a unit test for the pass and failure paths.
4. Keep the case deterministic and offline. Do not call a model.

## Why no live model

Live model evaluation requires a credential, a budget, and a stable fixture repository. It is deliberately excluded from the default suite and from CI. The three real-repository pilots provide the manual evidence path; see `docs/pilots/README.md`.

## Relationship to `ote verify`

- `ote verify` runs the project's own checks from `.ote/config.toml`.
- `ote eval` checks that the profile and its generated data are internally consistent.

They are complementary: a project can pass its tests while the shipped catalog or contracts are broken.

## References

- `docs/verification/README.md`
- `docs/catalog/README.md`
- `docs/pilots/README.md`
- `tests/evals/cases.json`
