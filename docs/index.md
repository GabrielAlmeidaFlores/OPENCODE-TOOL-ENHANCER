# OPENCODE-TOOL-ENHANCER

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally; CI green on run 43273061721

A reproducible OpenCode profile built around four pillars:

| Pillar | What it provides |
|---|---|
| Environment | OpenCode V2 configuration, agents, commands, skills, Ralph hats, installer, `ote` CLI |
| Orchestration | Ralph as the loop owner, coordinator delegation, risk-based gates |
| Intelligence | ripgrep, ast-grep, Serena, CodeGraph, Markdown memory, spec artifacts |
| Optimization | Deterministic verification, governance budgets, cost/token reporting, evals |

## Start here

```bash
git clone https://github.com/GabrielAlmeidaFlores/OPENCODE-TOOL-ENHANCER.git
cd OPENCODE-TOOL-ENHANCER
uv tool install ./packages/ote_cli
ote doctor
ote install --profile minimal --target /path/to/project --apply
```

- [OpenCode installation](installation/opencode.md)
- [Install the CLI](installation/ote-cli.md)
- [CLI reference](cli/README.md)
- [Profiles](profiles/README.md)

## What is verified

| Area | State |
|---|---|
| Static validation | 287 checks, including provenance, permissions, comments, and docs status |
| Test suite | 259 offline tests on Ubuntu and macOS |
| CLI | Wheel build, install lifecycle, profile/catalog verification, verification gates |
| Catalog | 34 generated artifacts with drift enforcement |
| Benchmarks | Deferred by decision; no published results |
| Pilots | Runner ready; execution pending |

Claims link to local evidence or a CI run. Vendor claims are labelled; no benchmark result is published without correctness and rework data.

## Design rules

1. Source and attribute every reusable artifact; do not invent agents, skills, or commands.
2. Never stage or commit automatically; the human decides.
3. Prefer descriptive names over comments; document only contracts.
4. Treat deterministic tools as the source of truth for correctness.
5. Keep the default profile minimal; enable optional tools explicitly.

Full rules: [AGENTS.md](https://github.com/GabrielAlmeidaFlores/OPENCODE-TOOL-ENHANCER/blob/main/AGENTS.md).

## Project

- [Architecture](architecture/overview.md)
- [Security](security/README.md)
- [Compatibility policy](compatibility/policy.md)
- [Provenance](provenance/README.md)
- [Release process](release/README.md)
- [Troubleshooting](troubleshooting/README.md)
