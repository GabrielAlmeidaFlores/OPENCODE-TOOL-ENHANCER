# ADR-004: Benchmarks are methodology and harness only

- Status: Accepted
- Date: 2026-11-11

## Context

Producing credible cost and quality numbers requires paid model runs on equivalent tasks, models, and repositories. No budget or provider credentials were supplied for this repository's authoring.

## Decision

Publish:

- A reproducible task set.
- A baseline configuration (stock OpenCode default agent).
- An optimized configuration (this repository).
- Metric definitions and a collection harness based on `opencode stats --json` and `opencode session export`.
- A results directory that explicitly states "no results yet".

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
5. Raw `opencode stats --json` artifacts committed under `benchmarks/results/<run-id>/`.
