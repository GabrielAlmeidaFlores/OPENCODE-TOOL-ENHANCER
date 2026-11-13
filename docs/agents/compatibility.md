# Artifact Compatibility

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally

This page records how the sourced artifacts behave in OpenCode 2.2.x. It separates static validation from runtime smoke tests so a passing check is not mistaken for a full evaluation. For GitHub Copilot, Claude Code, and OpenAI GPT/Codex mappings, see [Platform Compatibility](../compatibility/README.md).

## Version matrix

Run `toolwright compat` for the OpenCode V1/V2 feature matrix. Cells that were not verified are marked `not verified`. The matrix records supported features only; it is not a performance or benchmark result.

## Agents

All twelve custom agents are discovered by `opencode debug agents`. The coordinator is primary; the other eleven are subagents.

| Agent | Mode | Edit permission | Runtime status |
| --- | --- | --- | --- |
| `coordinator` | primary | denied | Verified with `opencode run --agent coordinator` |
| `planner` | subagent | denied | Loaded and permission-validated |
| `researcher` | subagent | denied | Used by the Ralph `research` collection |
| `architect` | subagent | denied | Loaded and permission-validated |
| `backend-developer` | subagent | allowed | Used by the Ralph `code-assist` collection |
| `frontend-developer` | subagent | allowed | Loaded and permission-validated |
| `database-specialist` | subagent | allowed | Loaded and permission-validated |
| `code-reviewer` | subagent | denied | Verified with `opencode run --agent code-reviewer` |
| `test-engineer` | subagent | allowed | Used by Ralph validation and benchmark verification |
| `security-reviewer` | subagent | denied | Loaded and permission-validated |
| `performance-analyst` | subagent | denied | Loaded and permission-validated |
| `documentation-engineer` | subagent | documentation only | Loaded and permission-validated |

## Commands

All commands have a valid `description` and target an existing agent. File installation is verified by the installer test.

| Command | Target agent | Static validation | Runtime smoke |
| --- | --- | --- | --- |
| `/implement` | `coordinator` | pass | verified on the TypeScript fixture |
| `/review` | `coordinator` | pass | verified on the TypeScript fixture |
| `/debug` | `coordinator` | pass | verified on the TypeScript fixture |
| `/security` | `security-reviewer` | pass | verified on the TypeScript fixture |
| `/docs` | `documentation-engineer` | pass | verified on the TypeScript fixture |
| `/refactor` | `backend-developer` | pass | verified on the TypeScript fixture |
| `/db` | `database-specialist` | pass | verified on the TypeScript fixture |
| `/perf` | `coordinator` | pass | verified on the TypeScript fixture |

The commands are sourced from `wshobson/agents`. Their Claude-specific task and checkpoint tool references were mapped to OpenCode `subagent`, `question`, and local agent names. Each command carries a local compatibility note.

## Skills

All skills have valid frontmatter, a matching directory name, author attribution, and supporting files where the upstream skill requires them.

| Skill | Supporting files | Status |
| --- | --- | --- |
| `test-driven-development` | `writing-good-tests.md` | copied; runtime skill call verified |
| `systematic-debugging` | references, example, script | copied; runtime skill call verified |
| `writing-plans` | none | copied; runtime skill call verified |
| `verification-before-completion` | none | copied; runtime skill call verified |
| `requesting-code-review` | `code-reviewer.md` | copied; runtime skill call verified |
| `api-design-principles` | references and assets | copied; runtime skill call verified |
| `database-migration` | references | copied; runtime skill call verified |
| `code-review-excellence` | references | copied; runtime skill call verified |
| `auth-implementation-patterns` | references | copied; runtime skill call verified |
| `changelog-automation` | references | copied; runtime skill call verified |

Runtime skill loading was verified for all ten skills: each smoke run called the `skill` tool and referenced the requested skill by name.

## Ralph collections

| Collection | Static validation | Runtime |
| --- | --- | --- |
| `research` | YAML valid, preflight pass | Completed in 2 iterations with `RESEARCH_COMPLETE` |
| `code-assist` | YAML valid, preflight pass | Longer multi-wave flow; needs a larger iteration budget |
| `review` | YAML valid, preflight pass | Dry-run only |
| `debug` | YAML valid, preflight pass | Dry-run only |

## MCP servers

| Server | Runtime status |
| --- | --- |
| `serena` | Connected in the test environment |
| `codegraph` | Connected in the test environment after `codegraph init` |
| `repomix` | Disabled by default |
| `jcodemunch` | Disabled by default |

## Known compatibility gaps

1. Command runtime smoke tests were run on the TypeScript fixture; the results are recorded in the command table.
2. Ralph `code-assist` needs a larger iteration budget and more stable event emission.
3. MCP startup depends on local binaries and language servers.
4. Windows is supported through WSL or Git Bash only.

## Verification commands

```bash
opencode debug agents
opencode run --agent code-reviewer "Reply with exactly: OK"
./scripts/validation/validate.sh
ralph preflight -c configs/ralph/ralph.yml --format human
```
