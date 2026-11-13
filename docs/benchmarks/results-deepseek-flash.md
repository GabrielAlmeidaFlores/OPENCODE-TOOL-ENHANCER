# DeepSeek Flash Benchmark Results

> **Status:** Experimental · **Last verified:** 2026-11-13 · **Evidence:** 30 isolated harness runs on `deepseek/deepseek-flash`; artifacts under `benchmarks/results/deepseek-flash-2026-11-13/`

## Result

The optimized configuration did **not** reduce cost on this task set. It used more tokens, cost more, and took longer than the baseline while producing the same verification outcome.

| Metric | Baseline | Optimized | Difference |
|---|---:|---:|---:|
| Total cost, 15 runs | $2.427892 | $2.573181 | +6.0% |
| Total input + output tokens | 6,802,876 | 7,176,372 | +5.5% |
| Total wall time | 906s | 1,244s | +37.3% |
| Verification failures | 0 / 15 | 0 / 15 | equal |
| Runs scored 4 | 14 | 11 | -3 |
| Runs scored 3 | 1 | 4 | +3 |

Do not present this configuration as a cost saving on these tasks.

## Setup

| Item | Value |
|---|---|
| Model | `deepseek/deepseek-flash` |
| OpenCode | `2.2.7` |
| Source commit | `a7983f8` (`v0.4.0`) |
| Task set | 5 tasks: validation, refactor, performance, security, C# validation |
| Repeats | 3 per task per arm |
| Total runs | 30 |
| Isolation | One disposable clone per run |
| Baseline | Stock OpenCode config, `build` agent |
| Optimized | `configs/opencode/opencode.jsonc`, `coordinator` agent, minimal installed profile |
| Hardware / OS | macOS 26.5.2, Apple silicon |

Each run started from a fresh copy of a prepared template. TypeScript dependencies were installed before the runs. A run wrote its own `benchmarks/results/<run-id>` directory, which was moved out before the clone was deleted, keeping `opencode stats --project .` scoped to one session.

## Per-task medians

| Task | Baseline cost | Optimized cost | Delta | Baseline tokens in/out | Optimized tokens in/out | Baseline wall | Optimized wall | Score baseline/optimized |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `cs-validation` | $0.199999 | $0.210411 | +5.2% | 478,381 / 75,808 | 496,123 / 80,769 | 99s | 79s | 4 / 4 |
| `ts-perf` | $0.163958 | $0.171099 | +4.4% | 392,660 / 63,278 | 413,486 / 66,447 | 40s | 94s | 4 / 3 |
| `ts-refactor` | $0.151943 | $0.156745 | +3.2% | 357,540 / 59,602 | 374,049 / 61,238 | 26s | 41s | 4 / 4 |
| `ts-security` | $0.176380 | $0.185834 | +5.4% | 429,894 / 68,222 | 449,641 / 71,326 | 41s | 75s | 4 / 4 |
| `ts-validation` | $0.135555 | $0.148191 | +9.3% | 312,968 / 53,023 | 341,671 / 58,087 | 74s | 62s | 4 / 3 |

The optimized arm was slower on four of five tasks. It was faster only on `cs-validation`, where the median wall time fell from 99s to 79s while cost still rose 5.2%.

## Correctness

All 30 verification commands passed.

| Arm | Score 4 | Score 3 | Score 2 | Score 1 | Score 0 |
|---|---:|---:|---:|---:|---:|
| Baseline | 14 | 1 | 0 | 0 | 0 |
| Optimized | 11 | 4 | 0 | 0 | 0 |

A score of 4 requires a passing verification command and changes inside the task's declared areas. Score 3 means verification passed but the run also changed an unrelated file.

- Baseline score-3 run: modified `examples/typescript/AGENTS.md`.
- Optimized score-3 runs: modified `examples/typescript/README.md` in 3 runs and `AGENTS.md` in 2 runs, with one run changing both.

These are scope deviations, not verification failures.

## Rework

The harness issues one prompt per run and does not implement follow-up cycles. Rework was therefore not exercised; every run records zero follow-up prompts by construction. This result says nothing about how much human intervention would be needed after reviewing the diffs.

## Interpretation

For these small, well-scoped tasks, the coordinator profile's extra planning, delegation, and tool activity outweighed any context savings. The optimized arm performed more steps and tool calls in every task:

| Task | Baseline steps | Optimized steps | Baseline tools | Optimized tools |
|---|---:|---:|---:|---:|
| `cs-validation` | 278 | 291 | 372 | 389 |
| `ts-perf` | 226 | 236 | 302 | 316 |
| `ts-refactor` | 206 | 216 | 278 | 288 |
| `ts-security` | 245 | 255 | 329 | 341 |
| `ts-validation` | 188 | 199 | 249 | 268 |

This is evidence against the current optimized configuration on this task set. It is not evidence that every optimized workflow is more expensive; larger or more ambiguous tasks may behave differently.

## Limitations

- One model only (`deepseek/deepseek-flash`), not a representative sample of model behavior.
- Small example repositories; coordinator overhead may dominate more than in larger codebases.
- Three repeats per task; report medians, not statistical significance.
- Correctness scores come from the verification command plus an automated changed-path scope check. There was no independent blind review.
- Rework and human intervention were not exercised.
- The tasks and examples were not changed during the benchmark.
- Cost depends on provider pricing at run time.
- `opencode stats` recorded per-run cost inside an isolated clone; session-level accounting was not independently reconciled.
- Optimized run metadata records the disposable fixture commit `a8eb1be` because the installed profile was committed into the clone. The source code under test is `a7983f8` in both arms.

## Artifacts

Every run directory contains:

- `meta.json`
- `stats.json`
- `session.jsonl`
- `export.json`
- `verification.log`
- `diff.patch`
- `status.txt`
- `notes.md`

Start at `benchmarks/results/deepseek-flash-2026-11-13/summary.json` or the per-run `notes.md`.

## References

- `docs/benchmarks/methodology.md`
- `benchmarks/harness/run.sh`
- `benchmarks/tasks/`
- `docs/installation/adapter-validation.md`
