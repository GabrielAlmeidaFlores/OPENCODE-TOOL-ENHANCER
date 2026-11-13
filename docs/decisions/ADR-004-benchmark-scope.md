# ADR-004: Benchmarks are methodology and harness only

- Status: Accepted
- Date: 2026-11-11

## Context

Producing credible cost and quality numbers requires paid model runs on equivalent tasks, models, and repositories. No budget or provider credentials were supplied for this repository's authoring.

## Decision

Publish:

- A reproducible task set.
- A baseline configuration: the stock default agent of the AI coding tool under test. The initial harness implements OpenCode; this is not a claim that the benchmark is OpenCode-only.
- An optimized configuration (this repository).
- Metric definitions and a collection harness. The current OpenCode harness derives per-run metrics from `session.jsonl`; other tools require an equivalent runner.
- A results directory that starts empty and accepts reproducible result sets.

Do **not** publish invented numbers, vendor figures presented as independent results, or token counts without quality outcomes.

## Consequences

- The repository makes no savings claim.
- Readers can run the harness with their own credentials and contribute results.
- Any contributed result must include model IDs, task IDs, correctness scoring, and rework counts.

## Acceptance for a valid result

1. Same repository commit and task definitions for baseline and optimized runs.
2. Same model and variant unless the experiment explicitly studies routing.
3. Correctness scored by tests plus a blind review rubric.
4. Rework and human interventions recorded.
5. Per-run artifacts committed under `benchmarks/results/<run-id>/`, including `run-stats.json` derived from the session log.


## Update 2026-11-13

- The benchmark question is tool-neutral: compare ToolWright against the stock configuration of the same AI coding tool.
- The first published run uses the OpenCode 2.2.7 reference adapter and `deepseek/deepseek-flash`. It is not a Claude, Copilot, or Codex result.
- Per-run cost and token values come from `run-stats.json`, not `opencode stats --project .`, because that command can aggregate sessions across runs that share a project identity.
- The optimized configuration did not reduce cost overall in the first result set. See the [DeepSeek Flash results](../benchmarks/results-deepseek-flash.md).
