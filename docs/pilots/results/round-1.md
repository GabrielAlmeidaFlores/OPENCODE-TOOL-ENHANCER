# Pilot Round 1 — Discovery Suite

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** real runs on pinned repositories; incomplete due provider limit

Read-only discovery tasks across the three selected repositories. These are **not** the five code-change tasks in the pilot procedure; they exercise analysis, planning, security review, refactor planning, and performance review. No source code was modified.

## Method

- Runner: `ote pilot run` with the `minimal` profile in a disposable clone.
- Model: `opencode/deepseek-v4.1-flash-free`.
- Verification: the named report must exist and contain at least three bullet or numbered items.
- Each task ran once. A failed task was recorded, not retried.
- Reports for passing tasks are under `docs/pilots/results/<repository>/`.

## Results

| Repository | Task | Category | Result | Failure class | OpenCode | Verify | Input | Output | Tools | Wall |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| honojs/hono | T1 | Bug analysis | fail | artifact-missing | 0 | 1 | 57934 | 1988 | 23 | 77.33s |
| honojs/hono | T2 | Feature proposal | fail | artifact-missing | 0 | 1 | 84245 | 4960 | 43 | 134.27s |
| honojs/hono | T3 | Refactor plan | pass | pass | 0 | 0 | 106500 | 6823 | 45 | 162.34s |
| honojs/hono | T4 | Security review | pass | pass | 0 | 0 | 184007 | 9400 | 56 | 295.53s |
| honojs/hono | T5 | Performance review | pass | pass | 0 | 0 | 128496 | 8867 | 40 | 123.37s |
| ardalis/CleanArchitecture | T1 | Bug analysis | fail | unsupported-input | 1 | 1 | 67758 | 5009 | 41 | 163.34s |
| ardalis/CleanArchitecture | T2 | Feature proposal | pass | pass | 0 | 0 | 40181 | 6401 | 52 | 138.46s |
| ardalis/CleanArchitecture | T3 | Refactor plan | pass | pass | 0 | 0 | 89937 | 7783 | 30 | 102.02s |
| ardalis/CleanArchitecture | T4 | Security review | pass | pass | 0 | 0 | 54528 | 8341 | 53 | 148.76s |
| ardalis/CleanArchitecture | T5 | Performance review | fail | provider-limit | 1 | 1 | 18130 | 861 | 5 | 22.92s |
| vercel/turborepo | T1 | Bug analysis | fail | provider-limit | 1 | 1 | 0 | 0 | 0 | 19.5s |
| vercel/turborepo | T2 | Feature proposal | fail | provider-limit | 1 | 1 | 0 | 0 | 0 | 17.66s |
| vercel/turborepo | T3 | Refactor plan | fail | provider-limit | 1 | 1 | 0 | 0 | 0 | 24.99s |
| vercel/turborepo | T4 | Security review | fail | provider-limit | 1 | 1 | 0 | 0 | 0 | 14.75s |
| vercel/turborepo | T5 | Performance review | fail | provider-limit | 1 | 1 | 0 | 0 | 0 | 15.37s |

## Summary

- Tasks attempted: 15
- Passed: 6
- Failed: 9
- Cost: $0.000000 (free model)
- Input tokens: 831716
- Output tokens: 60433
- Tool calls: 388
- Wall time: 1453s

## Failure analysis

| Class | Count | Cause |
| --- | ---: | --- |
| `artifact-missing` | 2 | Hono bug/feature runs completed but produced no report file |
| `unsupported-input` | 1 | CleanArchitecture bug run requested Web Search, which the non-interactive run could not answer |
| `provider-limit` | 6 | Free-model quota exhausted during CleanArchitecture task 5 and all turborepo tasks |

## Correctness and rework

Correctness here means the report exists and passes the structural check. The six passing reports were spot-checked for real `file:line` references, but they were not independently reviewed by a second agent or human.

Rework required:

- Rerun Hono bug and feature tasks with a stricter output instruction or a larger completion budget.
- Rerun CleanArchitecture bug and performance tasks with a model that can complete without Web Search.
- Rerun all turborepo tasks when the free quota resets or a funded model is approved.

## Limitations

- Read-only discovery, not implementation; no code-change correctness is claimed.
- One run per task; no statistical comparison.
- Free-model quota was exhausted mid-round; turborepo has no data.
- Web Search was unavailable in the non-interactive runner.
- Reports are model output and may contain incorrect file references.

## Next round

1. Define the five code-change tasks per repository with deterministic verification commands.
2. Install project dependencies once per repository and reuse a base cache.
3. Execute with a model budget or after the free quota resets.
4. Review every diff independently and record rework and human interventions.

## References

- `docs/pilots/README.md`
- `docs/pilots/results/hono-smoke.md`
