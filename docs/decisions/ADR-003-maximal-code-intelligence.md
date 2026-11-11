# ADR-003: Maximal code-intelligence default with overhead guards

- Status: Accepted
- Date: 2026-11-11

## Context

The requested default is maximal coverage: ast-grep, Serena, and CodeGraph in addition to native tools and ripgrep. MCP servers and large tool catalogs consume context, so enabling everything without controls contradicts the project's cost objective.

Verified facts:

| Tool | Version | License | Integration |
| --- | --- | --- | --- |
| ast-grep | 0.51.1 (0.51.2 available 2026-11-11) | MIT | CLI |
| Serena | 2.1.0 (2026-10-19) | GPL-3.0-or-later (SolidLSP MIT) | MCP |
| CodeGraph | active, MIT | MIT | MCP (`codegraph serve --mcp`) |
| ripgrep | installed | MIT/Unlicense | CLI/native |
| Repomix | active | MIT | CLI/MCP (optional) |
| jCodeMunch | active | dual-use, commercial license required | MCP (optional) |
| Universal Ctags | 6.2.1 | GPL-2.0 | CLI (optional) |

## Decision

Ship a maximal default but enforce these guards:

1. MCP servers use V2 **Code Mode** (default) and short unique names.
2. `permissions` deny unused `<server>_<tool>` actions rather than disconnecting servers.
3. Serena runs with `--context ide` to avoid duplicating basic read/search tools.
4. CodeGraph is enabled only after `codegraph init`; it keeps a local SQLite graph and a single writer.
5. A `minimal` profile is provided for small repositories or constrained budgets.
6. Repomix, jCodeMunch, Ctags, Graphify, and Aider repo maps remain optional and are not installed by default.

## Consequences

- Initial install and indexing have a real time and disk cost, which is documented.
- The maximal profile is not recommended for repositories under roughly 50 files; use the minimal profile.
- License obligations: Serena is GPL-3.0-or-later and is installed externally; jCodeMunch requires a paid commercial license when used commercially.

## Vendor-claim policy

Vendor benchmarks (for example jCodeMunch's "96.2% fewer tokens per lookup") are recorded as vendor claims, not independently verified results. This repository publishes no savings figures until the benchmark harness has been run.

## References

- https://github.com/ast-grep/ast-grep
- https://github.com/oraios/serena
- https://github.com/colbymchenry/codegraph
- https://github.com/yamadashy/repomix
- https://github.com/jgravelle/jcodemunch-mcp
- https://github.com/universal-ctags/ctags
