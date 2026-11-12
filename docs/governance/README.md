# Governance

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally and in CI run 43252608149

Governance makes long agent runs auditable without adding a daemon or a second runtime. The CLI evaluates limits deterministically and reports violations; it does not intercept tool calls at runtime.

## What is enforced

| Area | Mechanism |
|---|---|
| Agent contracts | Derived from `agents/*/AGENT.md` mode and permissions |
| Budgets | `[governance]` limits in `.ote/config.toml` |
| Loop detection | Repeated actions above `max_repeats` |
| Deadlock detection | Handoff bounces above `max_bounces` |
| Risk gates | Required gates per risk level |
| Validator mode | `off`, `advisory`, or `strict`, recorded with each evaluation |

## Contracts

```bash
ote govern contracts
ote govern contracts --json
```

Each contract reports the agent's mode, whether it is read-only, its allowed and denied actions, and any violation:

- the coordinator must be `primary`;
- every specialist must be `subagent`;
- read-only roles must deny `edit`;
- writer roles must allow `edit`.

Read-only roles: `coordinator`, `planner`, `researcher`, `architect`, `code-reviewer`, `security-reviewer`, `performance-analyst`.

## Budgets

```toml
[governance]
validator_mode = "advisory"
max_iterations = 40
max_tool_calls = 200
max_writes = 15
max_cost_usd = 5.0
max_delegation_depth = 2
max_repeats = 2
max_bounces = 3
```

Missing values fall back to the documented defaults.

## Evaluating a run

Provide a JSON record:

```json
{
  "iterations": 12,
  "tool_calls": 80,
  "writes": 4,
  "cost_usd": 1.25,
  "delegation_depth": 1,
  "repeats": 0,
  "bounces": 0
}
```

```bash
ote govern check --record run.json
ote govern check --record run.json --json
```

Exit code 1 means the record is blocked. Each violation names its kind: `budget`, `loop`, or `deadlock`.

## Risk gates

```bash
ote govern gate --risk low
ote govern gate --risk medium
ote govern gate --risk high
```

| Risk | Required gates |
|---|---|
| `low` | `verify` |
| `medium` | `verify`, `review` |
| `high` | `verify`, `review`, `security` |

## Validator modes

- `off` — the mode is recorded and no runtime enforcement is expected.
- `advisory` — a violation is reported and the caller decides whether to continue.
- `strict` — a violation must block the run in the calling orchestrator.

`ote govern check` always evaluates and returns exit code 1 on a violation, independent of the
recorded mode. Interpreting the mode is the caller's responsibility; runtime interception belongs
to the orchestrator. The current integration point is `ote govern check` plus the Ralph finalizer's
`ote verify` step.

## Limitations

- This is policy evaluation, not a security sandbox. The OpenCode permission model remains defense-in-depth.
- Budget and loop values must be supplied by the caller or the orchestrator; the CLI does not read model usage by itself.
- Risk gates describe required steps; they do not execute reviewer agents automatically.

## Design reference

The governance concepts follow `DVNghiem/FlowDeck`'s documented contract validator, budgets, and loop/deadlock detection (MIT). The verification cache follows `juanmanueldaza/nerv`'s exec-cache idea (Apache-2.0). The implementation is original Python; see the `verification-and-governance` entry in `docs/provenance/registry.yml`.

## References

- `docs/verification/README.md`
- `docs/orchestration/ralph.md`
- `AGENTS.md` Sections 2B and 14
