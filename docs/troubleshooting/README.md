# Troubleshooting

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

## Windows

OpenCode ships Windows binaries, but the scripts in this repository target POSIX shells. Use WSL or Git Bash. Paths in MCP commands and `external_directory` rules must use the platform's format.

## Getting help

- OpenCode issues: https://github.com/anomalyco/opencode/issues
- Ralph issues: https://github.com/mikeyobrien/ralph-orchestrator/issues
- Serena issues: https://github.com/oraios/serena/issues
- CodeGraph issues: https://github.com/colbymchenry/codegraph/issues
