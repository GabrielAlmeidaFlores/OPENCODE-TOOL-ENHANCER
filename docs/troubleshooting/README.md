# Troubleshooting

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally

## OpenCode

| Symptom | Cause | Fix |
| --- | --- | --- |
| `default_agent` ignored, Build starts | Coordinator agent not discovered | Copy `agents/coordinator/AGENT.md` to `.opencode/agents/coordinator.md`; run `opencode debug agents` |
| Agent can edit when it should not | A later permission rule allows it | Rules are ordered, last match wins. Inspect with `opencode debug agent <name>` |
| `.env` readable | A later `read` allow rule overrides the deny | Move the deny to the end of the array |
| Config rejected | Unsupported or malformed V2 field | Validate against `https://opencode.ai/config.json` |
| Context overflows quickly | `tool_output` too high or compaction disabled | Lower caps; keep `compaction.auto: true` |
| No LSP diagnostics | V2 does not run language servers | Use Serena or project lint/typecheck commands |

## MCP

| Symptom | Cause | Fix |
| --- | --- | --- |
| `mcp list` says "No MCP servers configured" but `.opencode/opencode.jsonc` exists | The directory is not a Git repository, so project discovery did not start there | Run from a Git worktree, or pass `OPENCODE_CONFIG=/abs/path/.opencode/opencode.jsonc` |
| Server stays `needs authentication` | OAuth not completed | Run `opencode mcp auth <name>` |
| Server disconnected | Binary not on `PATH` | Use an absolute command path |
| Startup timeout | Slow language server or index | Raise `mcp.servers.<name>.timeout.startup` |
| Tool list is huge | Code Mode disabled or too many servers | Keep `codemode: true`; disable optional servers |
| `codegraph` writer lock | Two MCP writers on one project | Run one; prefer the daemon |

## Serena

| Symptom | Cause | Fix |
| --- | --- | --- |
| `serena: command not found` | `uv tool` bin directory not on `PATH` | Add `~/.local/bin` or use the absolute path |
| Symbol search fails | Language server missing | Install the language server for your stack |
| High memory | Multiple language servers | Limit languages or disable Serena for this project |

## ast-grep

| Symptom | Cause | Fix |
| --- | --- | --- |
| Pattern does not match | Wrong language flag | Add `-l ts`, `-l py`, etc. |
| Parse error on file | Unsupported syntax version | Update ast-grep |
| Rewrite changes formatting | Expected | Run without `-U` first and review |

## Ralph

| Symptom | Cause | Fix |
| --- | --- | --- |
| `No AI agents detected` | OpenCode not on `PATH` | `which opencode` |
| Loop never completes | Finalizer did not emit the promise | Inspect `.ralph/agent/scratchpad.md`; check the finalizer instruction |
| Gate passes despite failures | Validator trusted the builder | Validator must execute commands itself |
| Per-hat agent ignored | `args` not forwarded | Use `backend.args` or the `args` alias; verify with a dry run |
| Cost page commands fail | Stale `--max-cost` flag | Use current `ralph run` flags; set limits in `event_loop` |

## Repository tooling

| Symptom | Cause | Fix |
| --- | --- | --- |
| `ote: command not found` | `~/.local/bin` is not on `PATH` | Export it, or run `PYTHONPATH=packages/ote_cli python3 -m ote_cli` |
| `ote install` says `already up to date` but files look old | Source digest still matches | Use `--force`, or change the artifact and re-run |
| `ote update --check` exits 1 | Managed files were edited or the source advanced | Inspect the reported paths; reinstall with `--force` after reviewing the edits |
| `ote uninstall` keeps a file | The file changed after installation | Review the change, then use `--force` if removal is intended |
| `ote doctor` fails on `opencode` | Missing or V1 installation | Install `@opencode/cli` 2.2.x |
| `ote doctor` warns about `serena` or `codegraph` | Optional tools are not installed | Install them only if the profile needs them |
| `ote` cannot find the repository | Running outside a checkout | Run from the checkout or set `OTE_REPO` |
| `validate.sh` fails on a new file | Required file list changed | Add the file and cover it with a test; see `docs/architecture/testing.md` |
| `make test` fails only in CI | Python version, missing PyYAML, CRLF checkout, or uncommitted files | See `docs/troubleshooting/ci.md` |
| CI job queued for hours | Runner availability or concurrency | Inspect with `gh run list`; see `docs/troubleshooting/ci.md` |
| Harness dry-run exits 2 | OpenCode missing on `PATH` | Fixed in Phase 1: dry-run needs only Python; real runs still need OpenCode |
| Docs page fails validation | Missing status block or non-ISO date | Add `Status`, `Last verified`, and `Evidence` near the title |
| ShellCheck fails after a script edit | Unquoted expansion or dead branch | Run `make lint` before returning the change |

## Windows

OpenCode ships Windows binaries, but the scripts in this repository target POSIX shells. Use WSL or Git Bash. Paths in MCP commands and `external_directory` rules must use the platform's format.

## Getting help

- This repository: https://github.com/GabrielAlmeidaFlores/OPENCODE-TOOL-ENHANCER/issues
- OpenCode issues: https://github.com/anomalyco/opencode/issues
- Ralph issues: https://github.com/mikeyobrien/ralph-orchestrator/issues
- Serena issues: https://github.com/oraios/serena/issues
- CodeGraph issues: https://github.com/colbymchenry/codegraph/issues
