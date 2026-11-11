# Benchmark Results

No results are published yet.

A result is accepted only if it includes:

- `meta.json` with commit, model ID and variant, arm, and task
- `stats.json` from `opencode stats --json --cost`
- `session.jsonl` from `opencode run --format json`
- `verification.log` with the acceptance command output
- `notes.md` with correctness, rework, and human interventions

Token counts without correctness and rework outcomes are not a result.

Run the harness:

```bash
./benchmarks/harness/run.sh --arm baseline  --task benchmarks/tasks/ts-validation.json
./benchmarks/harness/run.sh --arm optimized --task benchmarks/tasks/ts-validation.json
```
