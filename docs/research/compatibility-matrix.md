# Compatibility Matrix

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally

Verified on 2026-11-11 against a standalone OpenCode 2.2.7 binary and repository sources. Nothing in this matrix was inferred from vendor marketing.

## OpenCode V2 CLI contract

| Capability | Verified | Notes |
| --- | --- | --- |
| `opencode run` | Yes | Positional message still supported |
| `--agent` | Yes | Used for per-hat routing |
| `--model provider/model#variant` | Yes | Variant syntax preserved |
| `--format json` | Yes | Useful for harness output |
| `opencode stats --cost --json` | Yes | Benchmark telemetry |
| `opencode mcp {list,add,auth,logout}` | Yes | No `debug` subcommand in V2 |
| `opencode debug agents` | Yes | V2 lists effective agent config |
| Native LSP | **No** | V2 does not run language servers |
| V1 config loading | Yes | Normalized in memory |

## Ralph ↔ OpenCode

| Item | Status | Evidence |
| --- | --- | --- |
| Backend name | `opencode` | Backend docs |
| Invocation | `opencode run "<prompt>"` | `crates/ralph-adapters/src/cli_backend.rs` |
| Streaming | Plain text only | Adapter sets `OutputFormat::Text` |
| Auto-detect priority | 8th | Backend docs |
| Per-hat args | Supported | `HatConfig.backend_args`, alias `args` |
| `--max-cost` | Not a current `ralph run` flag | CLI reference; cost page is stale |

## Tool compatibility

| Tool | Integration | Requires | License | Default |
| --- | --- | --- | --- | --- |
| ripgrep | CLI/native search | none | MIT/Unlicense | Yes |
| ast-grep 0.51.1 | CLI | `ast-grep` binary | MIT | Yes |
| Serena 2.1.0 | MCP stdio | `uv`, language servers | GPL-3.0-or-later | Yes |
| CodeGraph | MCP stdio | `codegraph` binary, `codegraph init` | MIT | Yes |
| Repomix | CLI/MCP | Node or Docker | MIT | Optional |
| jCodeMunch | MCP | `uv`/`pipx` | Commercial for paid use | Optional |
| Universal Ctags | CLI | `ctags` | GPL-2.0 | Optional |

## Known incompatibilities

1. OpenCode V2 has no `lsp` permission action or LSP tool.
2. Ralph's OpenCode backend does not stream structured events, so gates must rely on exit codes.
3. CodeGraph allows one MCP writer per project; do not launch two `serve --mcp` processes with `CODEGRAPH_NO_DAEMON=1`.
