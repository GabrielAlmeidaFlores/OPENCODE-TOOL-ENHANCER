# Benchmark Methodology

> **Status:** Stable · **Last verified:** 2026-11-13 · **Evidence:** harness verified locally; one result set published

Status: methodology, harness, and one published DeepSeek Flash result set.

## Question

Does the optimized configuration complete the same tasks correctly at a lower total cost than the stock configuration of the same AI coding tool, without more rework?

Token reduction alone is not a valid result.

The question is tool-neutral. It applies to OpenCode, Claude Code, GitHub Copilot, ChatGPT/Codex, or any other AI coding tool. The current executable harness implements the OpenCode reference adapter; other tools require an equivalent runner and an equivalent stock baseline for that tool. Do not treat an OpenCode result as a cross-tool result.

## Configurations

| Arm | Definition |
| --- | --- |
| Baseline | Stock configuration of the tool under test; in the current harness, OpenCode with the default `build` agent and no custom MCP servers |
| Optimized | ToolWright configuration for the same tool; in the current harness, [`configs/opencode/opencode.jsonc`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/configs/opencode/opencode.jsonc) with `coordinator` and the full toolset |

Both arms use the same tool, repository commit, model ID and variant, and task definitions. Comparing different tools requires a separate experiment with each tool's own stock baseline.

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
3. Run the tool's stock baseline arm. Capture the session export and the per-run summary derived from `session.jsonl`. For the OpenCode harness, treat `opencode stats --project .` as cumulative when runs share a project identity; do not use it as a per-run value.
4. Reset the working tree. Run the optimized arm.
5. Score correctness with the verification command plus a blind review rubric.
6. Record rework: follow-up prompts, failed gates, human interventions.
7. Repeat each task at least three times to expose variance.

## Scoring

| Metric | Source |
| --- | --- |
| Input/output tokens | `run-stats.json` derived from `session.jsonl` |
| Cost | `run-stats.json` derived from `session.jsonl` |
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

For an agent-assisted run, use the sourced `perf` command ([`commands/perf.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/commands/perf.md)) or run the harness directly.


The current harness does not call a model by itself; it assumes `opencode run` is configured and authenticated. It records artifacts and refuses to overwrite an existing run ID. A Claude, Copilot, or Codex run needs an equivalent runner that uses that tool's stock baseline and exposes the same per-run metrics.

## Results

Place results in `benchmarks/results/<run-id>/` with:

- `meta.json` (commit, model, arm, task)
- `stats.json` (raw `opencode stats` snapshot)
- `run-stats.json` (per-run values derived from the session log)
- `export.json`
- `verification.log`
- `notes.md`

The first result set is published at [`docs/benchmarks/results-deepseek-flash.md`](results-deepseek-flash.md). It reports 30 isolated runs across 5 tasks, 2 arms, and 3 repeats with `deepseek/deepseek-flash`.

The optimized configuration did not reduce cost overall in that OpenCode result set, although it was cheaper on two of five tasks. Do not generalize that mixed result to other models, tools, adapters, or task sizes without running the appropriate harness.

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
