# Benchmark Methodology

The full methodology is maintained at [docs/benchmarks/methodology.md](../../docs/benchmarks/methodology.md).

This directory holds the executable side:

- `../tasks/` — task definitions (JSON, no parser dependency)
- `../harness/` — runner
- `../baseline/` — stock configuration arm
- `../results/` — contributed results

The first result set is published at `../../docs/benchmarks/results-deepseek-flash.md`. A valid result requires correctness and rework data, not only token counts.
