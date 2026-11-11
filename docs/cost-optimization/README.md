# Cost Optimization

The objective is the lowest total cost for a correct result, not the smallest prompt.

## Levers in this repository

| Lever | Setting | Effect |
| --- | --- | --- |
| Bounded retention | `compaction.keep.tokens: 12000` | Keeps recent context without replaying the session |
| Reserve | `compaction.buffer: 15%` | Leaves room before overflow |
| Output caps | `tool_output` 2000 lines / 51200 bytes | Prevents one command from dominating context |
| Delegation rules | Coordinator + role table | Avoids duplicate investigation |
| No recursive agents | `subagent_depth: 1` | Prevents agent fan-out |
| MCP Code Mode | `codemode: true` | Groups tools to reduce schema overhead |
| Optional servers disabled | `disabled: true` | No cost until enabled |
| Memory budget | `memories.budget: 2000` | Bounds injected memory |
| Iteration ceiling | `event_loop.max_iterations: 40` | Bounds runaway loops |
| Deterministic gates | tests, lint, typecheck | No model tokens for verification |
| Model routing | overlay | Cheap models for mechanical work |
| Minimal profile | no MCP | Removes server startup and schema cost |

## Anti-patterns

- Loading a whole repository with Repomix for a one-file change.
- Enabling every MCP server "just in case".
- Letting two agents investigate the same question.
- Re-running the full test suite after every small edit.
- Raising iteration limits to compensate for a vague prompt.
- Buying token savings by skipping tests.

## Measurement

Use `opencode stats --json --cost --project .` and record:

- input tokens
- output tokens
- total cost
- model calls
- tool calls
- iterations
- wall time
- test pass rate
- rework and human interventions

See [benchmark methodology](../benchmarks/methodology.md) and [cost observability](observability.md).

## Warning on vendor claims

Vendor benchmark numbers are not reproduced here. Do not repeat them as established facts. Measure on your own repository with your own model and tasks.
