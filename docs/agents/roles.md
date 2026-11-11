# Agent Roles and Delegation

## Provenance

All twelve role definitions are adapted from maintained MIT-licensed collections. The role-to-source mapping is in [docs/provenance/registry.yml](../provenance/registry.yml). Do not add a role without a source and a registry entry.

## Custom primary agent

`coordinator` is the primary agent. It is not OpenCode's default Build agent.

Responsibilities:

- Convert the request into acceptance criteria.
- Choose between direct work and delegation.
- Pass minimal, sufficient context.
- Enforce independent verification.
- Report evidence, not confidence.

The coordinator cannot edit files. This is deliberate: it prevents the orchestrator from silently doing implementation work and losing its review perspective.

## Subagents

| Agent | Invoke when | Do not invoke when |
| --- | --- | --- |
| `planner` | More than one verifiable step, or unclear order | Single-file, obvious change |
| `researcher` | Unknown library behavior, architecture discovery | The answer is already in the diff |
| `architect` | New module boundary, public contract, data ownership | Local refactor |
| `backend-developer` | Server, API, CLI, or business logic change | Pure UI work |
| `frontend-developer` | Component, page, state, or styling change | Backend-only change |
| `database-specialist` | Schema, index, migration, query plan | In-memory data change |
| `code-reviewer` | Any non-trivial diff | Trivial typo fix |
| `test-engineer` | Missing coverage or a reproducible defect | Reviewer already added a failing test |
| `security-reviewer` | Auth, input, files, network, secrets, new deps | Pure visual change |
| `performance-analyst` | Measured regression or hot path | Speculative optimization |
| `documentation-engineer` | Behavior or configuration changed | Internal refactor with no user impact |

## Delegation rules

1. **One owner per file.** Do not run two writing agents on the same path.
2. **Sequential by default.** Parallel agents are allowed only for disjoint areas and read-only work.
3. **No duplicate investigation.** If the coordinator already read the file, pass the relevant lines instead of asking an agent to rediscover them.
4. **No recursive spawning.** Subagents cannot launch subagents.
5. **Evidence required.** Every specialist returns `file:line` references and the commands it ran.
6. **Stop on ambiguity.** If the task needs a product decision, ask the human instead of inventing one.

## Verification chain

```text
implementation -> code-reviewer -> test-engineer -> (security-reviewer) -> coordinator
```

`security-reviewer` is mandatory for authentication, authorization, input parsing, file handling, outbound requests, secrets, and new dependencies.

## Ralph mapping

The official Ralph collections route to these agents with `backend.args`:

| Collection | Hat | Agent |
| --- | --- | --- |
| `code-assist` | planner | `planner` |
| `code-assist` | builder | `backend-developer` (or `frontend-developer` in a local copy) |
| `code-assist` | critic | `code-reviewer` |
| `code-assist` | finalizer | `coordinator` |
| `review` | reviewer | `code-reviewer` |
| `review` | analyzer | `security-reviewer` |
| `review` | closer | `coordinator` |
| `research` | researcher | `researcher` |
| `research` | synthesizer | `coordinator` |
| `debug` | investigator | `researcher` |
| `debug` | tester | `test-engineer` |
| `debug` | fixer | `backend-developer` |
| `debug` | verifier | `test-engineer` |

Ralph owns the loop and gates; OpenCode owns the agent behavior and tools.
