# Pilot Round 1 — Discovery Suite

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** real runs on pinned repositories; all 15 tasks passed after funded reruns

Read-only discovery tasks across the three selected repositories. These are **not** the five code-change tasks in the pilot procedure; they exercise analysis, planning, security review, refactor planning, and performance review. No source code was modified.

## Method

- Runner: `toolwright pilot run` with the `minimal` profile in a disposable clone.
- First attempt used `opencode/deepseek-v4.1-flash-free`; nine tasks failed on step limits or free-quota exhaustion.
- Failed tasks were rerun with the funded `deepseek/deepseek-flash` and the `backend-developer` agent directly.
- Coordinator and backend-developer step limits were raised (40 and 60) after the first attempt.
- Verification: the named report must exist and contain at least three bullet or numbered items.
- Reports for every task are under `docs/pilots/results/<repository>/`.

## Results

| Repository | Task | Category | Agent | Result | Input | Output | Tools | Wall | Cost |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| honojs/hono | T1 | Bug analysis | backend-developer | pass | 39441 | 2965 | 31 | 153.06s | $0.020911 |
| honojs/hono | T2 | Feature proposal | backend-developer | pass | 8028 | 956 | 6 | 25.57s | $0.002582 |
| honojs/hono | T3 | Refactor plan | ? | pass | 106500 | 6823 | 45 | 162.34s | $0.000000 |
| honojs/hono | T4 | Security review | ? | pass | 184007 | 9400 | 56 | 295.53s | $0.000000 |
| honojs/hono | T5 | Performance review | ? | pass | 128496 | 8867 | 40 | 123.37s | $0.000000 |
| ardalis/CleanArchitecture | T1 | Bug analysis | backend-developer | pass | 22032 | 2248 | 17 | 78.74s | $0.010568 |
| ardalis/CleanArchitecture | T2 | Feature proposal | ? | pass | 40181 | 6401 | 52 | 138.46s | $0.000000 |
| ardalis/CleanArchitecture | T3 | Refactor plan | ? | pass | 89937 | 7783 | 30 | 102.02s | $0.000000 |
| ardalis/CleanArchitecture | T4 | Security review | ? | pass | 54528 | 8341 | 53 | 148.76s | $0.000000 |
| ardalis/CleanArchitecture | T5 | Performance review | backend-developer | pass | 11289 | 1491 | 10 | 25.51s | $0.003045 |
| vercel/turborepo | T1 | Bug analysis | backend-developer | pass | 61945 | 2216 | 17 | 112.16s | $0.018977 |
| vercel/turborepo | T2 | Feature proposal | backend-developer | pass | 14434 | 1662 | 14 | 71.79s | $0.004855 |
| vercel/turborepo | T3 | Refactor plan | backend-developer | pass | 8193 | 1092 | 5 | 29.43s | $0.002497 |
| vercel/turborepo | T4 | Security review | backend-developer | pass | 37796 | 2555 | 17 | 77.82s | $0.010689 |
| vercel/turborepo | T5 | Performance review | backend-developer | pass | 18104 | 2678 | 15 | 47.79s | $0.005579 |

## Summary

- Tasks: 15
- Passed: 15
- Failed: 0
- Cost: $0.079705
- Input tokens: 824911
- Output tokens: 65478
- Tool calls: 408
- Wall time: 1585s

## Rework and failure history

| Initial failure | Count | Resolution |
| --- | ---: | --- |
| `artifact-missing` | 2 | Rerun with a bounded prompt and the backend agent |
| `unsupported-input` | 1 | Rerun without the Web Search request |
| `provider-limit` | 6 | Rerun with the funded DeepSeek model |
| Step limit | 2 | Raised coordinator/backend step budgets and shortened prompts |

Nine tasks were rerun. The reruns are the published result; the initial failures remain part of the rework record.

## Correctness

Correctness here means the report exists, passes the structural check, and references real `file:line` locations. The reports were spot-checked but not independently reviewed by a second agent or human. No code-change correctness is claimed.

## Limitations

- Read-only discovery, not implementation.
- One run per task; no statistical comparison.
- The paid reruns cost money; the original free attempts did not.
- Reports are model output and may contain incorrect analysis.
- Turborepo tasks used analysis only; no build or test execution.

## Next round

1. Define the five code-change tasks per repository with deterministic verification commands.
2. Install project dependencies once per repository and reuse a base cache.
3. Execute with an approved model budget.
4. Review every diff independently and record rework and human interventions.

## References

- [`docs/pilots/README.md`](../README.md)
- [`docs/pilots/results/hono-smoke.md`](hono-smoke.md)
