# GitHub Copilot

> **Status:** Experimental · **Last verified:** 2026-11-13 · **Evidence:** instructions checked against GitHub documentation; not runtime-tested

GitHub Copilot reads repository instructions from `.github/copilot-instructions.md`, path-specific files under `.github/instructions/`, and the nearest `AGENTS.md`. Copilot does not use OpenCode agents or permissions, so treat the mapping as guidance rather than an orchestration runtime.

## Files

| File | Scope |
|---|---|
| `.github/copilot-instructions.md` | Repository-wide rules |
| `.github/instructions/<name>.instructions.md` | Rules for matching paths; requires `applyTo` frontmatter |
| `AGENTS.md` | Agent instructions; the nearest file wins |
| `.github/prompts/<name>.prompt.md` | Reusable prompt files in supported IDE clients |

## Map the ToolWright agents

| ToolWright role | Copilot representation |
|---|---|
| `coordinator` | Repository instructions: plan, delegate, verify |
| `planner` | Prompt file or path instruction for planning |
| `code-reviewer` | Path instruction for changed source files |
| `security-reviewer` | Path instruction for security-sensitive paths |
| `test-engineer` | Path instruction for test files and verification commands |
| `documentation-engineer` | Path instruction for `docs/**` |

## Repository-wide example

```markdown
# .github/copilot-instructions.md

- Run `make validate`, `make test`, and `make lint` before proposing a change.
- Never stage or commit automatically. Leave changes unstaged.
- Prefer the existing agent, command, and skill contracts over new abstractions.
- Do not claim runtime behavior that was not executed.
```

## Path-specific example

```markdown
---
applyTo: "**/*.{ts,tsx,cs}"
---
Review for correctness, behavior changes, missing tests, and security issues.
Return findings in severity order with file and line references. Do not edit files.
```

## Mapping from ToolWright

1. Copy the project rules from `AGENTS.md` into `.github/copilot-instructions.md` or keep them in `AGENTS.md`.
2. Copy the relevant `agents/<role>/AGENT.md` body into an instruction file, removing OpenCode frontmatter and permission fields.
3. Convert `commands/*.md` into `.github/prompts/*.prompt.md` where the IDE supports prompt files.
4. Keep verification commands identical to the repository's `Makefile` or CI.

## Limits

- Copilot does not enforce OpenCode's per-agent edit/shell permissions.
- Copilot does not provide Ralph orchestration or ToolWright's subagent tree.
- Runtime availability of prompt files and path instructions varies by Copilot client and plan.
- This guide was checked against the documented formats, not executed in ToolWright CI.

## Verify

After opening the repository in a supported client, ask Copilot to summarize the repository instructions and confirm that `.github/copilot-instructions.md` or the nearest `AGENTS.md` appears in its references.

## References

- [GitHub Docs: repository custom instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- [AGENTS.md](https://agents.md)
