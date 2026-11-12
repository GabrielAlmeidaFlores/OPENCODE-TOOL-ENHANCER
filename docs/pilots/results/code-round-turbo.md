# turborepo Code-Change Pilot

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** 1/5 tasks passed; remaining tasks blocked by provider quota

Five TypeScript tasks in `packages/turbo-ignore` on `vercel/turborepo` at `4e3bdf1ef8`. Rust tooling was unavailable, so the round targeted the JavaScript package.

## Results

| Task | Change | Result | Verification |
|---|---|---|---|
| Feature | Add `--dry-run` to turbo-ignore | Passed | Jest: 76 tests |
| Feature | Add `--json` output | Blocked mid-run by free quota | Base Jest suite passed; change incomplete |
| Refactor | Extract decision formatting helper | Blocked by free quota | No code run |
| Security | Validate empty/malformed git refs | Blocked by free quota | No code run |
| Performance | Cache git result within one CLI run | Blocked by free quota | No code run |

Only task 1 is a completed code change. Tasks 2–5 did not produce verified implementations; no pass is claimed.

## Limitations

- Rust toolchain absent; no Rust crates were built or tested.
- Free-model quota was exhausted after task 1.
- Jest suites passed for tasks 2–5 but on incomplete or unchanged code, so those results are not correctness evidence.
- Diffs were not independently reviewed.

## Environment

- Setup: `corepack pnpm install --frozen-lockfile`
- Verification: `cd packages/turbo-ignore && corepack pnpm exec jest --runInBand`

## References

- `docs/pilots/results/round-1.md`
- `docs/pilots/results/turbo/`
