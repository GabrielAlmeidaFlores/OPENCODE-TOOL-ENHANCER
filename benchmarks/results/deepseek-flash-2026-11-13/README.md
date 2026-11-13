# DeepSeek Flash Result Set

Run date: 2026-11-13.

- Model: `deepseek/deepseek-flash`
- AI tool under test: OpenCode `2.2.7` (reference adapter only; Claude, Copilot, and Codex were not measured)
- Source commit: `a7983f8`
- Tasks: 5
- Arms: baseline, optimized
- Repeats: 3
- Runs: 30

Aggregate result: the optimized arm cost 14.2% more overall, used 2.3% more tokens, and took 37.3% longer. It was cheaper on C# validation and TypeScript validation, and more expensive on performance, refactor, and security. All 30 verification commands passed. This is an OpenCode reference-adapter result; it is not a claim about Claude, Copilot, or Codex.

Full analysis, per-task medians, correctness scoring, and limitations: [DeepSeek Flash results](../../../docs/benchmarks/results-deepseek-flash.md).

Each `r<repeat>-<arm>-<task>/` directory contains `meta.json`, `stats.json`, `run-stats.json`, `session.jsonl`, `export.json`, `verification.log`, `diff.patch`, `status.txt`, and `notes.md`.
