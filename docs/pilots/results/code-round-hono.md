# Hono Code-Change Pilot

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** targeted tests passed; diffs reviewed locally, not independently

Five code-change tasks on `honojs/hono` at `f6fbaf029a`. Each ran in a disposable clone with `pnpm install --frozen-lockfile`, the `minimal` profile, and the `backend-developer` agent.

## Results

| Task | Change | Files | Verification | Cost | Tokens in/out |
|---|---|---|---|---|---|
| Bug | Merge old and new `Set-Cookie` headers in `Context.res` | `src/context.ts`, `src/context.test.ts` | `vp test --run src/context.test.ts` | $0.028110 | 50,809 / 6,209 |
| Feature | Add `trustIncoming` option to `requestId` | `src/middleware/request-id/request-id.ts`, test | targeted request-id test | $0.004882 | 13,233 / 2,998 |
| Refactor | Extract bearer-token helpers into `src/middleware/jwt/bearer.ts` | `jwt.ts`, `jwk.ts`, new `bearer.ts` | jwt and jwk suites | $0.016989 | 37,154 / 6,421 |
| Security | Percent-encode CR/LF in `c.redirect` Location | `src/context.ts`, `src/context.test.ts` | context suite | $0.007498 | 18,360 / 2,261 |
| Performance | Cache query parsing per `Request` | `src/request.ts`, `src/request.test.ts` | request suite | $0.016334 | 33,995 / 4,851 |

All five had `opencode_exit = 0` and `verification_exit = 0` on the published run.

## Rework

- The security task first ended with an unavailable Web Search request after its tests passed. It was rerun with Web Search forbidden and then succeeded.
- No other task was retried.

## Review notes

- Diffs were inspected for scope: each touches only the named files plus tests (the refactor adds one helper file).
- Targeted type-check and test commands passed.
- No full repository suite was run for every task.
- A second human or agent review of the diffs is still required before treating these as production-ready changes.

## Limitations

- One repository; CleanArchitecture and turborepo code-change rounds are not executed.
- Free/paid mix: this round used the funded DeepSeek model.
- The fixes are pilot artifacts; they were not proposed upstream or committed to the project checkout.

## References

- `docs/pilots/results/round-1.md`
- `docs/pilots/README.md`
