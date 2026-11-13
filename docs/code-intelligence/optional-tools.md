# Optional Tools

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally

These are documented, not installed by default. Each adds a real cost; enable only with a specific need.

## Repomix

- https://github.com/yamadashy/repomix — MIT
- Packs a repository into one AI-friendly file; `--compress` uses tree-sitter.
- Useful for whole-repository analysis or generating a snapshot.
- Counterproductive as a default for targeted edits: it injects a large payload.
- MCP mode: `npx -y repomix --mcp --sandbox` (sandbox confines file access).

## jCodeMunch

- https://github.com/jgravelle/jcodemunch-mcp
- Symbol retrieval over MCP; tree-sitter indexing.
- **License:** free for personal use; commercial use requires a paid license.
- Vendor claim: 96.2% fewer tokens per lookup versus grep-and-read. This is a vendor benchmark and has not been independently reproduced here.
- Use only if Serena/CodeGraph do not cover your language or workflow.

## Universal Ctags

- https://github.com/universal-ctags/ctags — GPL-2.0
- Generates a tags index for fast symbol lookup from editors and scripts.
- No MCP integration; useful as a local, deterministic index.
- Weaker semantic depth than Serena.

## Graphify

- Active project: https://github.com/Graphify-Labs/graphify
- The URL `github.com/graphify` does **not** point to the maintained code-graph project.
- Skill/cloud product; vendor claims large token reductions without independent verification.
- Keep optional; evaluate on your own repository before adopting.

## Aider repository map

- https://github.com/Aider-AI/aider
- The repo map is part of Aider, not a standalone adapter integration.
- Not adopted. `rg`, ast-grep, Serena, and CodeGraph cover the same ground with clearer integration.

## Decision rule

Add a tool only if it answers a question the current stack cannot, and measure startup time, schema size, and output size before making it a default.
