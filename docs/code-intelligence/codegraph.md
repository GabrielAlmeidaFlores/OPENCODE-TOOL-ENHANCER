# CodeGraph

A local, pre-indexed code knowledge graph exposed over MCP. Use it for structural questions across files.

- Repository: https://github.com/colbymchenry/codegraph
- License: MIT
- Integration: MCP stdio
- Index: `.codegraph/` (local SQLite)

## Install

```bash
# Standalone installer (no Node required)
curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh

# or
npm i -g @colbymchenry/codegraph

codegraph --version
```

Open a new terminal after the standalone installer so `codegraph` resolves.

## Configure OpenCode manually

Prefer manual configuration so the installer does not rewrite unrelated settings:

```jsonc
{
  "mcp": {
    "servers": {
      "codegraph": {
        "type": "local",
        "command": ["codegraph", "serve", "--mcp"],
        "codemode": true,
        "timeout": { "startup": 60000 }
      }
    }
  }
}
```

Then index each project:

```bash
cd your-project
codegraph init
```

`codegraph init` creates `.codegraph/` and builds the graph. Auto-sync keeps it current.

## Verify

```bash
ls .codegraph
opencode mcp list
```

## What it answers

- Who calls this function?
- What does this module depend on?
- What is the blast radius of a change?
- Which files own a package?

## Strengths

- Cross-file structure without reading files.
- Local, no API keys, MIT license.
- Auto-sync avoids stale answers during edits.

## Limits

- Indexing cost on first run and on very large repositories.
- One active MCP writer per project. Do not run two direct `serve --mcp` processes with `CODEGRAPH_NO_DAEMON=1`.
- Graph quality depends on language parsing coverage.

## When not to use

- Very small repositories; `rg` and Serena are enough.
- Repositories you cannot write to (the index needs `.codegraph/`).
- When another graph server is already indexing the same tree.

## Token implications

Graph queries return structured, bounded answers, often cheaper than reading files. The index itself is not injected into the prompt.
