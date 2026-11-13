# Platform Compatibility

> **Status:** Experimental · **Last verified:** 2026-11-13 · **Evidence:** official file formats checked; OpenCode verified locally, other mappings documented but not CI-tested

ToolWright is native on OpenCode. The agents, commands, skills, and project rules are plain Markdown, so they can be mapped onto GitHub Copilot, Claude Code, and OpenAI GPT/Codex without rewriting the content.

## Support levels

| Platform | Level | What ToolWright provides | Verified here |
|---|---|---|---|
| OpenCode 2.2.x | Native | Configuration, agents, commands, skills, MCP servers, Ralph integration, installer | Yes, CI and local runs |
| GitHub Copilot | Portable | Repository instructions, path instructions, `AGENTS.md`, prompt files | File formats checked against GitHub documentation; not runtime-tested |
| Claude Code | Portable | `CLAUDE.md`, `.claude/agents/`, skills, commands | File formats checked against Claude documentation; not runtime-tested |
| OpenAI GPT / Codex | Portable | `AGENTS.md`, `.codex/agents/*.toml`, global instructions, ChatGPT project instructions | File formats checked against OpenAI documentation; not runtime-tested |

## What is portable

- **Project rules** from `AGENTS.md`, including Git safety, provenance, and documentation-comment rules.
- **Agent responsibilities** from `agents/<role>/AGENT.md`: coordinator, planner, researchers, developers, reviewers, test and security roles.
- **Commands** from `commands/*.md`.
- **Skills** from `skills/<name>/SKILL.md` where the target supports skills.
- **Model routing intent** (strong model for planning, economical model for routine work), expressed per platform.

## What is not portable

- OpenCode agent permissions (`edit`, `shell`, `subagent`, `webfetch`).
- OpenCode subagent spawning and per-agent step limits.
- Ralph Orchestrator's OpenCode backend and auto-commit behavior.
- ToolWright's installer lock and backup lifecycle, which targets OpenCode directories.
- MCP server definitions, unless the target platform supports the same MCP transport.

Do not claim a platform is verified just because its instruction file exists. Runtime behavior differs by client, model, and account plan.

## Guides

- [OpenCode](opencode.md) — native installation and verification.
- [GitHub Copilot](github-copilot.md) — `.github/copilot-instructions.md`, path instructions, `AGENTS.md`, prompt files.
- [Claude Code](claude.md) — `CLAUDE.md`, project subagents, skills, commands.
- [OpenAI GPT / Codex](openai-gpt.md) — `AGENTS.md`, custom agent TOML files, ChatGPT instructions.
- [Compatibility policy](policy.md) — supported targets and change rules.

## References

- GitHub Docs: [Adding repository custom instructions for GitHub Copilot](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- Claude Docs: [Create custom subagents](https://code.claude.com/docs/en/sub-agents)
- OpenAI Docs: [Custom instructions with AGENTS.md](https://developers.openai.com/codex/agent-configuration/agents-md)
- OpenAI Docs: [Subagents](https://developers.openai.com/codex/agent-configuration/subagents)
- OpenCode Docs: [Agents](https://opencode.ai/docs/agents)
