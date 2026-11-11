Repository: https://github.com/GabrielAlmeidaFlores/OPENCODE-TOOL-ENHANCER

# Install OpenCode V2 and this configuration

## Prerequisites

- macOS or Linux (Windows best-effort)
- `git`, `node` >= 20, `python3`
- A provider credential configured with `opencode auth login` or an environment variable

## 1. Install or upgrade OpenCode

```bash
npm install -g @opencode/cli
opencode --version
```

Expected: `2.2.x`.

If you have a V1 install, back up `~/.config/opencode` first:

```bash
./scripts/maintenance/backup-config.sh
```

If you already have an installation, add `--clean` to replace managed agents, commands, skills, and hat collections without leaving removed files behind:

```bash
./scripts/installation/install.sh --apply --clean --only opencode,agents,commands,skills,ralph
```

## 2. Add the project configuration

```bash
mkdir -p .opencode/agents .opencode/commands .opencode/skills
cp configs/opencode/opencode.jsonc .opencode/opencode.jsonc
```

Copy agents, commands, and skills:

```bash
for f in agents/*/AGENT.md; do
  role=$(basename "$(dirname "$f")")
  cp "$f" ".opencode/agents/$role.md"
done

cp commands/*.md .opencode/commands/
cp -R skills/* .opencode/skills/
```

## 3. Configure MCP servers

The repository config already references Serena and CodeGraph. Install them before starting OpenCode, or set `disabled: true` until they are ready.

See [code-intelligence.md](code-intelligence.md).

## 4. Verify

```bash
opencode debug config      # lists configuration sources
opencode debug agents      # lists effective agents and permissions
opencode mcp list
```

Expected: `coordinator` and eleven subagents are listed; configured MCP servers show `connected`, or `disabled` when intentionally opted out.

## 5. Select the agent

Start OpenCode and choose `coordinator`, or run:

```bash
opencode run --agent coordinator "Summarize this repository and propose the next task"
```

## Configuration options

| Option | Default | Change when |
| --- | --- | --- |
| `default_agent` | `coordinator` | You want a different primary agent |
| `compaction.keep.tokens` | `12000` | Your model has a small or very large window |
| `tool_output.max_bytes` | `51200` | You routinely need larger command output |
| `experimental.subagent_depth` | `1` | Never raise it without a specific need |
| `mcp.servers.*.disabled` | varies | You want to opt into an optional server |

## Common problems

| Problem | Fix |
| --- | --- |
| `default_agent` falls back to `build` | The `coordinator` file is missing from `.opencode/agents/` |
| MCP server shows disconnected | Check the binary is on `PATH` and raise `startup` timeout |
| Agent ignores permissions | A later rule wins; inspect with `opencode debug agent coordinator` |
| Config rejected | Validate against `https://opencode.ai/config.json` |

## Rollback

```bash
./scripts/maintenance/restore-config.sh
```

## References

- https://opencode.ai/docs/
- https://opencode.ai/docs/config
- https://opencode.ai/docs/agents
- https://opencode.ai/docs/mcp-servers
