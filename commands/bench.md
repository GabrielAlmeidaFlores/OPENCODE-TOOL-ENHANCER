---
description: Run the cost/quality benchmark harness for a task set
agent: coordinator
---

Benchmark scope: $ARGUMENTS

Follow `docs/benchmarks/methodology.md`. Confirm the repository commit, task IDs, model ID, and variant. Run the baseline and optimized configurations separately. Collect `opencode stats --json --cost` and `opencode session export` artifacts. Do not claim token savings without correctness and rework outcomes.
