# OpenAI GPT and Codex

> **Status:** Experimental · **Last verified:** 2026-11-13 · **Evidence:** Codex CLI 0.146.0 loaded the generated `AGENTS.md` through `codex debug prompt-input`; custom agent TOML fields match the documented schema, discovery not runtime-tested

OpenAI Codex reads `AGENTS.md` files before working and supports project-scoped custom agents as TOML files. ChatGPT desktop and Codex can run subagent workflows; ChatGPT projects and custom instructions carry the same project rules in chat contexts.

## Install with ToolWright

```bash
toolwright install --platform codex --profile minimal --target /path/to/project --apply
```

Update with the same command and remove with:

```bash
toolwright uninstall --target /path/to/project --apply --yes
```

The lock records each generated path, its generator, and its digest. Existing destination files are backed up before the adapter overwrites them.

## Generated files

| Path | Source |
|---|---|
| `AGENTS.md` | `AGENTS.md` |
| `.codex/agents/<role>.toml` | `agents/<role>/AGENT.md` |

Each custom agent file defines `name`, `description`, and `developer_instructions`, the three required fields in the Codex custom agent schema. Names use underscores, for example `code_reviewer`.

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
developer_instructions = """
You are an independent code reviewer. Do not edit files.
Report findings in severity order with file and line references.
Verify claims against the code and do not invent problems.
"""
```

Place the file at `.codex/agents/code_reviewer.toml`. Codex identifies the agent by its `name` field. The adapter omits `model` and `model_reasoning_effort`, so Codex inherits the parent session's settings. Add those fields only when you intentionally want the agent to override them.

## Role mapping

| ToolWright agent | Codex representation |
|---|---|
| `coordinator` | Main session plus `AGENTS.md` delegation rules |
| `planner` | Custom agent whose instructions request planning only |
| `researcher` | Custom agent whose instructions request read-heavy exploration |
| `code-reviewer` | Custom agent whose instructions request read-only review |
| `security-reviewer` | Custom agent focused on security findings |
| `backend-developer` | Execution-focused custom agent |
| `test-engineer` | Execution-focused custom agent with test commands |
| `documentation-engineer` | Documentation-only custom agent |

Codex custom agents inherit the parent session's sandbox, approvals, provider, and MCP servers. They cannot override those settings. The adapter does not set `sandbox_mode`; read-only intent lives in the instructions and is not a sandbox guarantee.

## Verify

Run this inside the generated target:

```bash
codex debug prompt-input "Summarize the repository instructions."
```

Codex CLI `0.146.0` returns the resolved prompt input as JSON. Search the output for `AGENTS.md` content such as the Git-safety rules to confirm that the project instructions load.

Custom agent discovery has no equivalent non-interactive inspection command. Confirm the TOML files parse and contain the required fields:

```bash
python3 - <<'PY'
import tomllib
from pathlib import Path
for path in sorted(Path(".codex/agents").glob("*.toml")):
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    missing = {"name", "description", "developer_instructions"} - set(data)
    print(path, "ok" if not missing else f"missing: {sorted(missing)}")
PY
```

## ChatGPT

ChatGPT does not read repository files automatically. Reuse the same rules by:

1. Adding the Git-safety, verification, and role rules to a Project's instructions.
2. Pasting the relevant role prompt into a conversation or custom GPT.
3. Keeping commands and repository paths explicit, because ChatGPT has no local checkout unless a tool provides one.

## Limits

- Codex custom agents are TOML, not the Markdown frontmatter used by OpenCode, Claude, and Copilot.
- OpenCode permission rules do not map directly to Codex sandbox settings.
- Ralph's OpenCode backend is not used by Codex.
- `AGENTS.md` loading was verified with Codex CLI `0.146.0`. Custom agent discovery was checked against the documented schema but not runtime-tested, because inspection requires an interactive `/agent` session or a model call.
- The adapter writes project-scoped files only. It does not modify `~/.codex/agents/` or `~/.codex/config.toml`.

## References

- [OpenAI Codex: Custom instructions with AGENTS.md](https://developers.openai.com/codex/guides/agents-md)
- [OpenAI Codex: Subagents](https://developers.openai.com/codex/subagents)
- [AGENTS.md](https://agents.md)
- `../installation/adapter-validation.md`
