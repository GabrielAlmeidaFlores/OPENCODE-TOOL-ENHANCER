# Platform Compatibility

> **Status:** Experimental · **Last verified:** 2026-11-13 · **Evidence:** installer-generated adapters validated on a real repository; OpenCode verified in CI; Copilot instruction and skill discovery plus Codex `AGENTS.md` loading checked with their CLIs; Claude Code runtime discovery unverified

ToolWright includes a fully verified OpenCode adapter. OpenCode is optional: the same agents, commands, skills, and project rules install as native files for GitHub Copilot, Claude Code, and OpenAI GPT/Codex.

## Support levels

| Platform | Level | What ToolWright provides | Verified here |
|---|---|---|---|
| OpenCode 2.2.x | Native adapter (reference) | Configuration, agents, commands, skills, MCP servers, Ralph integration, installer | Yes, CI and local runs |
| GitHub Copilot | Installer-generated adapter | `.github/copilot-instructions.md`, `.github/instructions/`, `.github/skills/`, `.github/prompts/`, `AGENTS.md` | Copilot CLI `1.0.105` discovers repository instructions, all 12 role instructions, and 10 project skills; prompt-file behavior not inspected |
| Claude Code | Installer-generated adapter | `CLAUDE.md`, `.claude/agents/`, `.claude/commands/`, `.claude/skills/` | File formats match the documented layout; Claude CLI was unavailable, so runtime discovery is unverified |
| OpenAI GPT / Codex | Installer-generated adapter | `AGENTS.md`, `.codex/agents/*.toml` | Codex CLI `0.146.0` loads `AGENTS.md`; custom agent files contain the required `name`, `description`, and `developer_instructions` fields; agent discovery was not runtime-tested |

## Install an adapter

```bash
toolwright install --platform opencode --profile minimal --target /path/to/project --apply
toolwright install --platform claude   --profile minimal --target /path/to/project --apply
toolwright install --platform copilot  --profile minimal --target /path/to/project --apply
toolwright install --platform codex    --profile minimal --target /path/to/project --apply
```

Use `toolwright profile use <profile> --platform <name>` for the same behavior through a profile. Non-OpenCode adapters generate files directly, back up overwritten destinations, and record every managed file in `toolwright.lock.json`. Remove them with `toolwright uninstall --target /path/to/project --apply --yes`.

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
- MCP server definitions, unless the target platform supports the same MCP transport.
- Identical orchestration behavior across clients; the generated files carry instructions, not a shared runtime.

The installer lock and uninstall lifecycle cover every adapter, but OpenCode still uses the shell installer while Claude, Copilot, and Codex write generated files directly.

Do not claim a platform is verified just because its instruction file exists. Runtime behavior differs by client, model, and account plan.

## Guides

- [OpenCode](opencode.md) — reference adapter installation and verification.
- [GitHub Copilot](github-copilot.md) — generated instructions, skills, prompts, and `AGENTS.md`.
- [Claude Code](claude.md) — generated `CLAUDE.md`, agents, commands, and skills.
- [OpenAI GPT / Codex](openai-gpt.md) — generated `AGENTS.md` and custom agent TOML files.
- [Adapter validation](../installation/adapter-validation.md) — deterministic install, update, and uninstall evidence.
- [Compatibility policy](policy.md) — supported targets and change rules.

## References

- GitHub Docs: [Adding repository custom instructions for GitHub Copilot](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- Claude Docs: [Create custom subagents](https://code.claude.com/docs/en/sub-agents)
- OpenAI Docs: [Custom instructions with AGENTS.md](https://developers.openai.com/codex/agent-configuration/agents-md)
- OpenAI Docs: [Subagents](https://developers.openai.com/codex/agent-configuration/subagents)
- OpenCode Docs: [Agents](https://opencode.ai/docs/agents)
