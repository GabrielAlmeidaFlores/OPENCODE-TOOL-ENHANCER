# MCP Overhead

This page records a narrow startup measurement performed on 2026-11-11 with OpenCode 2.2.7 on macOS arm64. It is not a token or task-cost benchmark.

## Method

- Isolated `HOME` directory with no global MCP configuration.
- Explicit project configuration for each profile.
- `opencode --standalone debug agents` executed twice per profile.
- `opencode --standalone mcp list` executed twice per profile.
- No model calls.

## Results

| Profile | `debug agents` run 1 | `debug agents` run 2 | `--standalone mcp list` |
| --- | ---: | ---: | ---: |
| Full profile | 2.04 s | 1.48 s | 0.15 s |
| Minimal profile | 1.46 s | 1.44 s | 0.16 s |

## Interpretation

- Configuration and agent loading adds roughly **0.0–0.6 s** in this environment when MCP servers are not connected.
- `--standalone mcp list` returns quickly because it lists configuration and does not complete a server handshake.
- Without `--standalone`, `mcp list` took about **20 s** for both profiles. That time is dominated by the background service and is not a useful discriminator between profiles.

## Limitations

The measurement does not include:

- Serena or CodeGraph handshake time.
- MCP tool-schema token overhead.
- Language-server indexing.
- Retrieval quality.
- Task cost or correctness.

Those require the deferred benchmark program. Do not present these startup numbers as token savings or as a complete overhead comparison.

## Reproduction

```bash
HOME=/tmp/opencode-overhead-home \
OPENCODE_CONFIG=/path/to/opencode.jsonc \
/usr/bin/time -p opencode --standalone debug agents
```
