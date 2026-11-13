# OpenAI GPT and Codex

> **Status:** Experimental · **Last verified:** 2026-11-13 · **Evidence:** file formats checked against OpenAI documentation; not runtime-tested

OpenAI Codex reads `AGENTS.md` files before working and supports project-scoped custom agents as TOML files. ChatGPT desktop and Codex can run subagent workflows; ChatGPT projects and custom instructions carry the same project rules in chat contexts.

## Files

| Path | Purpose |
|---|---|
| `AGENTS.md` | Repository guidance read by Codex |
| `AGENTS.override.md` | Optional override at the same directory level |
| `~/.codex/AGENTS.md` | Global guidance for every repository |
| `.codex/agents/<name>.toml` | Project-scoped custom agent |
| `~/.codex/agents/<name>.toml` | User-scoped custom agent |
| `.codex/config.toml` | Agent concurrency and defaults |

## Custom agent example

```toml
name = "code_reviewer"
description = "Reviews changes for correctness, regressions, security, and missing tests."
model = "gpt-6.1-sol"
model_reasoning_effort = "high"
developer_instructions = """
You are an independent code reviewer. Do not edit files.
Report findings in severity order with file and line references.
Verify claims against the code and do not invent problems.
"""
```

Place the file at `.codex/agents/code-reviewer.toml`. Codex identifies the agent by its `name` field.

## Role mapping

| ToolWright agent | Codex representation |
|---|---|
| `coordinator` | Main session plus `AGENTS.md` delegation rules |
| `planner` | Read-only custom agent with high reasoning effort |
| `researcher` | Read-heavy custom agent |
| `code-reviewer` | Read-only custom agent |
| `security-reviewer` | Read-only custom agent focused on security |
| `backend-developer` | Execution-focused custom agent |
| `test-engineer` | Execution-focused custom agent with test commands |
| `documentation-engineer` | Documentation-only custom agent |

Codex custom agents inherit the parent session's sandbox, approvals, provider, and MCP servers. They cannot override those settings.

## ChatGPT

ChatGPT does not read repository files automatically. Reuse the same rules by:

1. Adding the Git-safety, verification, and role rules to a Project's instructions.
2. Pasting the relevant role prompt into a conversation or custom GPT.
3. Keeping commands and repository paths explicit, because ChatGPT has no local checkout unless a tool provides one.

## Limits

- Codex custom agents are TOML, not the Markdown frontmatter used by OpenCode, Claude, and Copilot.
- OpenCode permission rules do not map directly to Codex sandbox settings.
- Ralph's OpenCode backend is not used by Codex.
- The mapping was checked against the documented format, not executed in ToolWright CI.

## References

- [OpenAI Codex: AGENTS.md](https://developers.openai.com/codex/agent-configuration/agents-md)
- [OpenAI Codex: Subagents and custom agents](https://developers.openai.com/codex/agent-configuration/subagents)
- [AGENTS.md](https://agents.md)
