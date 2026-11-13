# Benchmark Results

The first published result set is `deepseek-flash-2026-11-13/`, summarized in `../../docs/benchmarks/results-deepseek-flash.md`.

A result is accepted only if it includes:

- `meta.json` with commit, model ID and variant, arm, and task
- `stats.json` from `opencode stats --json --cost`
- `session.jsonl` from `opencode run --format json`
- `verification.log` with the acceptance command output
- `notes.md` with correctness, rework, and human interventions

Token counts without correctness and rework outcomes are not a result.

Run the harness:

```bash
OPENCODE_BENCH_MODEL=provider/model ./benchmarks/harness/run.sh --arm baseline  --task benchmarks/tasks/ts-validation.json
OPENCODE_BENCH_MODEL=provider/model ./benchmarks/harness/run.sh --arm optimized --task benchmarks/tasks/ts-validation.json
```
