# Artifact Compatibility

This page records how the sourced artifacts behave in OpenCode 2.2.x. It separates static validation from runtime smoke tests so a passing check is not mistaken for a full evaluation.

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
| `/implement` | `coordinator` | pass | pending |
| `/review` | `coordinator` | pass | pending |
| `/debug` | `coordinator` | pass | pending |
| `/security` | `security-reviewer` | pass | pending |
| `/docs` | `documentation-engineer` | pass | pending |
| `/refactor` | `backend-developer` | pass | pending |
| `/db` | `database-specialist` | pass | pending |
| `/perf` | `performance-analyst` | pass | pending |

The commands are sourced from `wshobson/agents`. Some upstream bodies reference specialist names from that collection. Each command carries a local note mapping those names to the agents in `docs/agents/roles.md`.

## Skills

All skills have valid frontmatter, a matching directory name, author attribution, and supporting files where the upstream skill requires them.

| Skill | Supporting files | Status |
| --- | --- | --- |
| `test-driven-development` | `writing-good-tests.md` | copied |
| `systematic-debugging` | references, example, script | copied |
| `writing-plans` | none | copied |
| `verification-before-completion` | none | copied |
| `requesting-code-review` | `code-reviewer.md` | copied |
| `api-design-principles` | references and assets | copied |
| `database-migration` | references | copied |
| `code-review-excellence` | references | copied |
| `auth-implementation-patterns` | references | copied |
| `changelog-automation` | references | copied |

Runtime skill loading is exercised through the skill tool; a dedicated automated smoke test is still pending.

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

1. Commands and skills still need per-command runtime smoke tests.
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
