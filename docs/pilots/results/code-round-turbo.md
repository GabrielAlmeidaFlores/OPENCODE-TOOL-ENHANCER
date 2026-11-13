# turborepo Code-Change Pilot

> **Status:** Experimental · **Last verified:** 2026-11-13 · **Evidence:** four of five tasks are production-ready after independent review; the performance task was rejected

Five TypeScript tasks in `packages/turbo-ignore` on `vercel/turborepo` at `4e3bdf1ef8`. Rust tooling was unavailable, so the round targeted the JavaScript package.

## Results

| Task | Change | Verification | Cost | Tokens in/out | Final verdict |
|---|---|---|---|---|---|
| Feature | Add `--dry-run` to turbo-ignore | Jest: 77 tests, 100% coverage | $0.000000 (free) | 62,784 / 5,351 | Production-ready |
| Feature | Add machine-readable `--json` output | Jest: 80 tests, 100% coverage; `tsc`, `oxfmt`, `oxlint` clean | $0.000000 (free) | 196,801 / 13,699 | Production-ready |
| Refactor | Extract decision logging into one helper module | Jest: 74 tests, 100% coverage | $0.000000 (free) | 43,675 / 1,001 | Production-ready |
| Security | Validate git refs and preserve fallback behavior | Jest: 80 tests, 100% coverage; `tsc`, `oxfmt`, `oxlint` clean | $0.000000 (free) | 128,520 / 10,088 | Production-ready |
| Performance | Cache git results within one CLI run | Jest: 79 tests, 98.74% branch coverage | $0.000000 (free) | 192,461 / 7,676 | Rejected |

The published task runs had `opencode_exit = 0` except task 4's third run, which hit a free-quota limit after producing the change; its final verification and cleanup were executed separately. Tasks 2 and 4 were rerun after review found defects.

## Independent review

A reviewer agent read every diff, ran the Jest suites, and checked the changed behavior. A final reviewer verified the last task 4 revision.

| Task | First verdict | Issue | Final result |
|---|---|---|---|
| `--dry-run` | Production-ready | CLI flag wiring is not covered by a test | Production-ready; advisory only |
| `--json` | Needs-fix | Output was prefixed and interleaved with human logs, so stdout was not valid JSON | Production-ready: one JSON object on stdout, logs on stderr, documented contract, stronger tests |
| Refactor | Reject | Shipped 22 unreferenced duplicate modules and 25 unused aliases | Production-ready: one helper module, no aliases |
| Security | Needs-fix | 98.74% branch coverage failed the 100% gate; a malformed SHA skipped the fallback | Production-ready: coverage, formatter, and linter pass; malformed SHA returns the fallback; malformed `--fallback` is caught and logged |
| Performance | Needs-fix | The cache cannot save a git call because each function has one caller; it added process-global mutable state and 45 alias exports | **Rejected**; no useful caching target exists in this CLI |

## Rework

- Task 2 was run three times: the first version was not valid JSON, the second lacked documentation, tests, and formatting, and the third passed all checks.
- Task 4 was run three times: the first missed the coverage gate, the second regressed the fallback path, and the third hit a free-quota limit after producing the change. A duplicate test title and an uncaught malformed `--fallback` were then fixed locally; a final independent review confirmed the result.

## Limitations

- Rust toolchain absent; no Rust crates were built or tested.
- The performance task premise was invalid for this code path. It is recorded as rejected rather than counted as a pass.
- Only the `turbo-ignore` package was exercised; workspace-wide builds were not run.
- The task 4 clone's recorded metadata marks the third run as unsuccessful because its inline verification hit a lint error; the final verification was rerun after the cleanup and passed.
- No change was proposed upstream or committed to the project checkout.

## Environment

- Setup: `corepack pnpm install --frozen-lockfile`
- Verification: `cd packages/turbo-ignore && corepack pnpm exec jest --runInBand`, plus `tsc --noEmit`, `oxfmt --check`, and `oxlint`.
- Tests use the package's existing Jest configuration, including its 100% coverage thresholds.

## References

- [`docs/pilots/results/round-1.md`](round-1.md)
- `docs/pilots/results/turbo/`
