---
name: performance-profile
description: Measure and improve performance with baselines and variance. Use when latency, throughput, memory, or cost regresses.
---

# Performance Profile

## Steps

1. Define the metric and the workload.
2. Capture a baseline with a reproducible command; run it more than once.
3. Profile the suspected path.
4. Identify the dominant cost: CPU, I/O, allocation, lock contention, or network.
5. Make one change.
6. Re-measure with the same workload and report variance.

## Rules

- No optimization without a baseline.
- Report p50 and p95/p99, not only the mean.
- Do not trade correctness for speed.
- Record hardware, runtime version, and dataset size.
- Do not benchmark in a noisy environment without noting it.

## Output

Metric, baseline, profile evidence, bottleneck, change, result, variance, and risks.
