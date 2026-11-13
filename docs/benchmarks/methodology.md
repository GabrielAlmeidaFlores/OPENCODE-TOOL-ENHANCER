# Benchmark Methodology

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally

Status: methodology and harness only. No results are published.

## Question

Does the optimized configuration complete the same tasks correctly at a lower total cost than the baseline, without more rework?

Token reduction alone is not a valid result.

## Configurations

| Arm | Definition |
| --- | --- |
| Baseline | Stock OpenCode, default Build agent, no custom MCP servers |
| Optimized | `configs/opencode/opencode.jsonc`, `coordinator`, full toolset |

Both arms use the same repository commit, the same model ID and variant, and the same task definitions.

## Task set

Task definitions live in `benchmarks/tasks/`. Each task declares:

- id, title, repository commit
- prompt
- acceptance criteria
- verification command
- working directory
- expected changed areas
- maximum allowed wall time

Start with 5 tasks covering: a small bug fix, a feature with tests, a refactor, a performance fix, and a security fix.

## Procedure

1. Freeze the repository at a commit. Record it. Run each task from its declared `working_directory`.
2. Record model ID, variant, and provider.
3. Run the baseline arm. Capture `opencode stats --json --cost` and `opencode session export`.
4. Reset the working tree. Run the optimized arm.
5. Score correctness with the verification command plus a blind review rubric.
6. Record rework: follow-up prompts, failed gates, human interventions.
7. Repeat each task at least three times to expose variance.

## Scoring

| Metric | Source |
| --- | --- |
| Input/output tokens | `opencode stats --json` |
| Cost | `opencode stats --json --cost` |
| Model calls | session export |
| Tool calls | session export |
| Iterations | session export |
| Wall time | harness timer |
| Test pass rate | verification command |
| Correctness | tests plus rubric |
| Rework | follow-up count |
| Human interventions | manual log |

## Validity rules

- A cheaper arm that fails correctness is a failure, not a saving.
- A faster arm that needs more rework is not a saving.
- Report medians and spread, not a single run.
- Disclose hardware, OS, and provider latency.

## Harness

```bash
OPENCODE_BENCH_MODEL=provider/model ./benchmarks/harness/run.sh --arm baseline --task benchmarks/tasks/ts-validation.json
OPENCODE_BENCH_MODEL=provider/model ./benchmarks/harness/run.sh --arm optimized --task benchmarks/tasks/ts-validation.json
```

For an agent-assisted run, use the sourced `perf` command (`commands/perf.md`) or run the harness directly.


The harness does not call a model by itself; it assumes `opencode run` is configured and authenticated. It records artifacts and refuses to overwrite an existing run ID.

## Results

Place results in `benchmarks/results/<run-id>/` with:

- `meta.json` (commit, model, arm, task)
- `stats.json`
- `export.json`
- `verification.log`
- `notes.md`

No results exist yet.

## Correctness and rework rubric

Every run is scored against the same rubric. Token and cost savings are only valid when the optimized arm meets or exceeds the baseline.

| Score | Correctness | Rework |
|---:|---|---|
| 4 | Verification command passes; behavior matches acceptance criteria; no unrelated changes | No follow-up required |
| 3 | Verification passes; minor non-blocking issue accepted by review | One small follow-up |
| 2 | Verification passes after one fix cycle | One failed gate or human correction |
| 1 | Verification still fails or behavior is incomplete | Multiple fix cycles |
| 0 | Incorrect, unsafe, or destructive result | Unbounded rework |

A run with a lower correctness score than the baseline is not a cost saving, even when it uses fewer tokens. Report the score and rework count beside every cost figure.
