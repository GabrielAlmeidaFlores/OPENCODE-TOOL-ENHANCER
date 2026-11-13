# Claude Code

> **Status:** Experimental · **Last verified:** 2026-11-13 · **Evidence:** generated file formats checked against Claude documentation; runtime discovery unverified because the Claude CLI was unavailable

Claude Code reads project memory from `CLAUDE.md` and discovers project subagents in `.claude/agents/`. ToolWright generates those files directly from the shared agent, command, and skill sources.

## Install with ToolWright

```bash
toolwright install --platform claude --profile minimal --target /path/to/project --apply
```

The Claude adapter always writes `CLAUDE.md` and writes agents, commands, and skills only when those components are selected.

## Generated files

| Path | Purpose | Source |
|---|---|---|
| `CLAUDE.md` | Project memory and working agreements | `AGENTS.md` |
| `.claude/agents/<role>.md` | Project-scoped subagent with `name`, `description`, and `tools` frontmatter | `agents/<role>/AGENT.md` |
| `.claude/commands/<name>.md` | Project command | `commands/<name>.md` |
| `.claude/skills/<name>/` | Project skill files | `skills/<name>/` |

Update the files with another `toolwright install --platform claude --apply`. Remove them with:

```bash
toolwright uninstall --target /path/to/project --apply --yes
```

The lock records each generated path, its generator, and its digest. Existing destination files are backed up before the adapter overwrites them.

## Files

| Path | Purpose |
|---|---|
| `CLAUDE.md` | Project memory and working agreements |
| `.claude/agents/<name>.md` | Project-scoped subagent |
| `~/.claude/agents/<name>.md` | User-scoped subagent |
| `.claude/skills/<name>/SKILL.md` | Project skill |
| `.claude/commands/<name>.md` | Project command |

## Convert an agent

The adapter performs this conversion automatically. ToolWright agents use OpenCode fields such as `mode`, `permissions`, and `steps`. Claude Code expects `name`, `description`, and optionally `tools` and `model`. The generated files set `name`, `description`, and `tools`, and omit `model` so Claude uses its configured default.

The example below shows the generated shape. Edit the installed file only when you need to customize it.

```markdown
---
name: code-reviewer
description: Reviews changes for correctness, regressions, security, and missing tests.
tools: Read, Grep, Glob
model: sonnet
---

You are an independent code reviewer. Do not edit files.
Report findings in severity order with file and line references.
Verify claims against the code and do not invent problems.
```

Use the body of `agents/code-reviewer/AGENT.md` as the system prompt after removing OpenCode frontmatter.

## Role mapping

| ToolWright agent | Claude representation | Generated tools |
|---|---|---|
| `coordinator` | Project subagent | `Read`, `Grep`, `Glob` |
| `planner` | Project subagent | `Read`, `Grep`, `Glob` |
| `researcher` | Project subagent | `Read`, `Grep`, `Glob` |
| `architect` | Project subagent | `Read`, `Grep`, `Glob` |
| `code-reviewer` | Project subagent | `Read`, `Grep`, `Glob` |
| `security-reviewer` | Project subagent | `Read`, `Grep`, `Glob` |
| `performance-analyst` | Project subagent | `Read`, `Grep`, `Glob` |
| `backend-developer` | Project subagent | `Read`, `Grep`, `Glob`, `Edit`, `Write`, `Bash` |
| `frontend-developer` | Project subagent | `Read`, `Grep`, `Glob`, `Edit`, `Write`, `Bash` |
| `database-specialist` | Project subagent | `Read`, `Grep`, `Glob`, `Edit`, `Write`, `Bash` |
| `test-engineer` | Project subagent | `Read`, `Grep`, `Glob`, `Edit`, `Write`, `Bash` |
| `documentation-engineer` | Project subagent | `Read`, `Grep`, `Glob`, `Edit`, `Write`, `Bash` |

Claude's `tools` field is an allowlist. It does not reproduce OpenCode's ordered permission rules exactly; review the resulting tool surface. The generated `documentation-engineer` receives write tools for the whole workspace, not only `docs/**`.

## Project memory

Keep the Git-safety and verification rules from `AGENTS.md` in `CLAUDE.md`:

```markdown
# CLAUDE.md

- Never run `git add`, `git commit`, `git stash`, or destructive Git commands unless explicitly asked.
- Run `make validate`, `make test`, and `make lint` before claiming completion.
- Do not present unexecuted checks as passes.
```

## Limits

- OpenCode permission expressions do not map one-to-one to Claude tool lists.
- Ralph's OpenCode backend is not used by Claude Code.
- The generated file layout matches the documented format, but the Claude CLI was not installed during validation. Runtime discovery of `CLAUDE.md`, agents, commands, and skills remains unverified.
- The adapter does not set a Claude model name; model routing stays under Claude configuration.

## References

- [Claude Docs: Create custom subagents](https://code.claude.com/docs/en/sub-agents)
- [Claude Docs: Memory](https://code.claude.com/docs/en/memory)
- [Claude Docs: Skills](https://code.claude.com/docs/en/skills)
- `../installation/adapter-validation.md`
