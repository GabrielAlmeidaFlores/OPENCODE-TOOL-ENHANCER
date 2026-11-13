# Claude Code

> **Status:** Experimental · **Last verified:** 2026-11-13 · **Evidence:** file formats checked against Claude documentation; not runtime-tested

Claude Code reads project memory from `CLAUDE.md` and discovers project subagents in `.claude/agents/`. ToolWright agent roles map cleanly because both use Markdown with YAML frontmatter and a system-prompt body.

## Files

| Path | Purpose |
|---|---|
| `CLAUDE.md` | Project memory and working agreements |
| `.claude/agents/<name>.md` | Project-scoped subagent |
| `~/.claude/agents/<name>.md` | User-scoped subagent |
| `.claude/skills/<name>/SKILL.md` | Project skill |
| `.claude/commands/<name>.md` | Project command |

## Convert an agent

ToolWright agents use OpenCode fields such as `mode`, `permissions`, and `steps`. Claude Code expects `name`, `description`, and optionally `tools` and `model`.

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

| ToolWright agent | Claude representation | Suggested tools |
|---|---|---|
| `coordinator` | Main session agent or `Agent(...)` allowlist | `Agent`, `Read`, `Grep`, `Glob`, `Bash` |
| `planner` | Read-only subagent | `Read`, `Grep`, `Glob` |
| `code-reviewer` | Read-only subagent | `Read`, `Grep`, `Glob` |
| `security-reviewer` | Read-only subagent | `Read`, `Grep`, `Glob` |
| `backend-developer` | Write-capable subagent | `Read`, `Edit`, `Write`, `Bash` |
| `test-engineer` | Write-capable subagent | `Read`, `Edit`, `Write`, `Bash` |
| `documentation-engineer` | Docs-only subagent | `Read`, `Edit`, `Write` on `docs/**` |

Claude's `tools` field is an allowlist. It does not reproduce OpenCode's ordered permission rules exactly; review the resulting tool surface.

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
- The mapping was checked against the documented format, not executed in ToolWright CI.

## References

- [Claude Docs: Create custom subagents](https://code.claude.com/docs/en/sub-agents)
- [Claude Docs: Memory](https://code.claude.com/docs/en/memory)
- [Claude Docs: Skills](https://code.claude.com/docs/en/skills)
