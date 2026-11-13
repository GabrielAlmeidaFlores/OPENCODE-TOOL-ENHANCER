# DeepSeek Flash Result Set

Run date: 2026-11-13.

- Model: `deepseek/deepseek-flash`
- OpenCode: `2.2.7`
- Source commit: `a7983f8`
- Tasks: 5
- Arms: baseline, optimized
- Repeats: 3
- Runs: 30

Aggregate result: the optimized arm cost 6.0% more, used 5.5% more tokens, and took 37.3% longer. All 30 verification commands passed.

Full analysis, per-task medians, correctness scoring, and limitations: [DeepSeek Flash results](../../../docs/benchmarks/results-deepseek-flash.md).

Each `r<repeat>-<arm>-<task>/` directory contains `meta.json`, `stats.json`, `session.jsonl`, `export.json`, `verification.log`, `diff.patch`, `status.txt`, and `notes.md`.
