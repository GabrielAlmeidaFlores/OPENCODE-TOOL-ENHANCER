Repository: https://github.com/GabrielAlmeidaFlores/toolwright

# Install Code Intelligence

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally

Install in this order. Each step has a verification command.

## 1. ripgrep

```bash
brew install ripgrep
rg --version
```

## 2. ast-grep

```bash
brew install ast-grep
ast-grep --version
```

Expected: `0.51.x` or newer.

Create `.sgconfig.yml` in the repository root if you want project rules:

```yaml
ruleDirs:
  - tools/ast-grep/rules
```

## 3. Serena

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install -p 3.13 serena-agent
serena init
serena --version
```

Verify the MCP command resolves:

```bash
serena start-mcp-server --help
```

Optional but recommended: confirm the language server for your stack works before relying on Serena.

## 4. CodeGraph

```bash
curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh
# open a new terminal
codegraph --version
```

Index the project:

```bash
cd your-project
codegraph init
ls .codegraph
```

Do **not** run `codegraph install` (which rewrites agent configurations) if you use the repository's MCP config. Wire it manually instead.

## 5. Verify through OpenCode

```bash
opencode mcp list
```

Expected:

```text
serena     connected
codegraph  connected
```

## Resource expectations

| Tool | Startup | Disk | Notes |
| --- | --- | --- | --- |
| ripgrep | instant | none | — |
| ast-grep | instant | none | — |
| Serena | seconds to tens of seconds | language-server caches | depends on language |
| CodeGraph | seconds on first index | `.codegraph/` grows with repository | one writer per project |

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `serena: command not found` in OpenCode | Use the absolute path in the MCP `command` |
| Serena startup timeout | Raise `mcp.servers.serena.timeout.startup` to 90000 |
| CodeGraph writer lock | Stop the second `serve --mcp`; prefer the daemon |
| ast-grep parse errors | Check the language flag and file extension |
| High memory | Disable CodeGraph or Serena for this project |

## References

- https://github.com/oraios/serena
- https://github.com/ast-grep/ast-grep
- https://github.com/colbymchenry/codegraph
- https://github.com/BurntSushi/ripgrep
