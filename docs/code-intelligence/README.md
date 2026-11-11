# Code Intelligence

The default stack answers different questions with the cheapest sufficient tool.

| Question | Tool |
| --- | --- |
| Where is this string, error, or config key? | `grep` / `rg` |
| Which files match this name? | `glob` / `rg --files` |
| Which code has this structure? | ast-grep |
| Where is this symbol defined or referenced? | Serena |
| What calls this / what breaks if I change it? | CodeGraph |

## Defaults

- ripgrep — installed, no MCP.
- ast-grep — CLI, no MCP.
- Serena — MCP, `--context ide`.
- CodeGraph — MCP, per-project index.

## Optional

Repomix, jCodeMunch, Universal Ctags, Graphify, and Aider repository maps are documented in [optional-tools.md](optional-tools.md). They are not installed by default.

## Overhead rules

1. One MCP server per concern. Do not add a second symbol server.
2. Use Code Mode and permission filtering instead of exposing every tool.
3. Index once; do not re-index on every prompt.
4. Disable the stack on small repositories; use the minimal profile.
5. Measure startup time before enabling a server in an interactive loop.

## Pages

- [ripgrep](ripgrep.md)
- [ast-grep](ast-grep.md)
- [Serena](serena.md)
- [CodeGraph](codegraph.md)
- [Optional tools](optional-tools.md)
