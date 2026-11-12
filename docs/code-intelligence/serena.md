# Serena

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally

Symbol-level retrieval, editing, and refactoring over the Model Context Protocol. Serena replaces native LSP for OpenCode V2.

- Repository: https://github.com/oraios/serena
- Version used: 2.1.0
- License: GPL-3.0-or-later (SolidLSP is MIT; the combined distribution is GPL)
- Integration: MCP stdio

## Install

```bash
# Prerequisite: uv
curl -LsSf https://astral.sh/uv/install.sh | sh

uv tool install -p 3.13 serena-agent
serena init
serena --help
```

Additional language-server dependencies may be required for some languages. See the Serena language support page.

## OpenCode configuration

```jsonc
{
  "mcp": {
    "servers": {
      "serena": {
        "type": "local",
        "command": ["serena", "start-mcp-server", "--context", "ide", "--project-from-cwd"],
        "codemode": true,
        "timeout": { "startup": 60000 }
      }
    }
  }
}
```

`--context ide` is the context Serena recommends for terminal agents such as OpenCode: it removes basic tools that OpenCode already provides, reducing duplication and schema overhead.

## Verify

```bash
opencode mcp list
```

Expect `serena  connected`. If startup times out, raise `startup` and confirm the language server for your project is installed.

## What it provides

- Find symbol and file symbol overview.
- Find references and implementations.
- Diagnostics from the language server.
- Symbol-level edit and rename.
- Persistent memories.

## Strengths

- Real semantic navigation instead of text matching.
- Works across a large set of languages through LSP.
- Rename and symbol edits are safer than search-and-replace.

## Limits

- Startup and memory cost of language servers.
- External dependency and type-hierarchy features are limited for some languages.
- Tool catalog is large; trim it through Serena configuration and OpenCode permissions.
- GPL-3.0-or-later obligations if you redistribute a combined work.

## When not to use

- Tiny repositories where `rg` is sufficient.
- Languages without a working language server in your environment.
- Environments where running a long-lived server is not permitted.

## Token implications

Serena reduces whole-file reads, but its tool definitions and responses still consume context. Use `--context ide`, deny unused tools, and prefer one targeted query over exploratory calls.
