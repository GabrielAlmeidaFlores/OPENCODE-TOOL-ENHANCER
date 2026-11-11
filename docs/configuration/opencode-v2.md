# OpenCode V2 Configuration

This page explains the configuration in `configs/opencode/opencode.jsonc`.

## Location and precedence

OpenCode reads, from lowest to highest precedence:

1. `~/.config/opencode/opencode.json(c)` — user defaults
2. `<project>/opencode.json(c)`
3. `<project>/.opencode/opencode.json(c)`
4. System/enterprise configuration

The repository uses `<project>/.opencode/opencode.jsonc` so the setup is project-scoped and reviewable in Git.

## Top-level settings used

| Key | Value | Reason |
| --- | --- | --- |
| `default_agent` | `coordinator` | Avoid relying on the default Build agent |
| `permissions` | ordered rules | Least privilege and destructive-command approval |
| `mcp.servers` | Serena, CodeGraph, optional Repomix/jCodeMunch | Code intelligence |
| `compaction` | `keep.tokens: 12000`, `buffer: 15%` | Bound retained context |
| `tool_output` | 2000 lines / 51200 bytes | Prevent output floods |
| `watcher.ignore` | generated/index directories | Avoid wasted turns |
| `experimental.todo` | `true` | Multi-step tracking |
| `experimental.subagent_depth` | `1` | No recursive agent spawning |

## Agents

Agents are Markdown files under `.opencode/agents/`. The repository keeps canonical copies in `agents/<role>/AGENT.md` and the installer flattens them.

V2 frontmatter fields used:

```yaml
---
description: What the agent does and when to use it
mode: primary | subagent | all
steps: 12
permissions:
  - action: edit
    resource: "*"
    effect: deny
---
```

Do not use V1 fields (`prompt`, `tools`, `permission`, `disable`, `maxSteps`) in new files. V2 translates V1 files, but mixing formats in one file causes the V1 fields to be ignored.

## Permissions

V2 uses one ordered array. The last matching rule wins. Common actions:

| Action | Covers |
| --- | --- |
| `shell` | Bash commands |
| `edit` | write, edit, patch |
| `subagent` | Child agents |
| `read`, `glob`, `grep` | Discovery tools |
| `webfetch`, `websearch` | Web tools |
| `skill` | Skill loading |
| `external_directory` | Paths outside the workspace |

The repository's global rules allow normal work, ask before `rm -rf`, force-push, and external paths, and deny `sudo` and `.env` reads.

> V2 default allows `external_directory`. We set it to `ask` to preserve V1 caution.

## MCP servers

```jsonc
"mcp": {
  "servers": {
    "serena": { "type": "local", "command": ["serena", "start-mcp-server", "--context", "ide", "--project-from-cwd"], "codemode": true },
    "codegraph": { "type": "local", "command": ["codegraph", "serve", "--mcp"], "codemode": true }
  }
}
```

- **Code Mode** is the V2 default and groups tools, reducing schema overhead.
- Optional servers are configured with `"disabled": true`; enable them deliberately.
- Server tools are named `<server>_<tool>`. Deny unused tools with `permissions` instead of disconnecting the server.

## Compaction and tool output

- `compaction.keep.tokens` retains a recent tail; it is not a turn count.
- `compaction.buffer` is the share of the model window kept free before compaction.
- `tool_output` caps what a single command can inject.

Do not enable `warming` unless you understand the cost: it sends periodic requests to keep a cache warm.

## Models and routing

No model is hardcoded. OpenCode uses the user's selected model by default.

For per-agent routing, merge `configs/opencode/model-routing.example.jsonc` after setting every referenced environment variable. Unset `{env:...}` becomes an empty string, which is invalid.

Recommended shape:

| Work | Model class |
| --- | --- |
| Planning, architecture | strongest reasoning |
| Implementation | balanced |
| Review, security | reasoning-capable |
| Documentation, mechanical | economical |

## Minimal profile

`configs/opencode/minimal.jsonc` disables MCP entirely. Use it for small repositories, constrained budgets, or when MCP startup dominates task time.

## Validate

```bash
opencode debug config      # configuration sources
opencode debug agents      # effective agent definitions
opencode mcp list
./scripts/validation/validate.sh
```

## References

- https://opencode.ai/docs/config
- https://opencode.ai/docs/agents
- https://opencode.ai/docs/permissions
- https://opencode.ai/docs/mcp-servers
- https://opencode.ai/docs/compaction
