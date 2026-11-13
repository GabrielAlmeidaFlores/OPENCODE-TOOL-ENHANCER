# Compatibility Policy

> **Status:** Stable · **Last verified:** 2026-11-13 · **Evidence:** matrix and CI checks verified locally

## Supported targets

| Target | Level | Notes |
|---|---|---|
| OpenCode `2.2.x` | Native adapter (optional) | Reference adapter; CI pins `@opencode/cli@2.2.7` |
| OpenCode `1.x` | No | Configuration shape differs; migration only |
| Ralph Orchestrator `2.10.x` | Native (OpenCode backend) | Auto-commit limitation documented |
| GitHub Copilot | Installer-generated adapter | Instructions and skills discovered by Copilot CLI `1.0.105`; prompt files not inspected |
| Claude Code | Installer-generated adapter | `claude doctor` passed on CLI `2.1.323`; no non-interactive discovery command, so runtime discovery unverified |
| OpenAI GPT / Codex | Installer-generated adapter | `AGENTS.md` loaded by Codex CLI `0.146.0`; custom agent discovery not runtime-tested |
| Python | 3.11+ | CLI and validator |
| macOS / Linux | Yes | Windows via WSL or Git Bash |

Native means ToolWright ships the runtime configuration and verifies it. Installer-generated means ToolWright writes the platform's documented files, tracks them in the lock, and supports update and uninstall; runtime discovery is claimed only for the checks listed in the table.

## Compatibility matrix

```bash
toolwright compat
toolwright compat --json
```

The matrix marks unverified cells as `not verified`. It records supported features, not performance.

## Change policy

- A breaking change to configuration, agent contracts, CLI commands, or catalog schema requires a minor or major version bump.
- Removal or rename of a public command requires one minor release of deprecation with a warning in `CHANGELOG.md`.
- Upstream pins are updated in the provenance registry and the catalog together.
- Generated files must be regenerated; CI fails on drift.
- OpenCode V1 is not reintroduced. A future major version may change the supported V2 line.

## Verification

| Check | Command |
|---|---|
| Static validation | `make validate` |
| Test suite | `make test` |
| OpenCode agent discovery | CI `opencode profile` job |
| OpenCode compatibility matrix | `toolwright compat` |
| Adapter install, update, and uninstall | `docs/installation/adapter-validation.md` |
| Copilot instruction discovery | `copilot instruction list` in a generated target |
| Copilot skill discovery | `copilot skill list` in a generated target |
| Codex instruction loading | `codex debug prompt-input "Summarize the repository instructions."` in a generated target |
| Catalog drift | `toolwright catalog verify --check-drift` |

## References

- `../agents/compatibility.md`
- `README.md`
- `github-copilot.md`
- `claude.md`
- `openai-gpt.md`
- `../decisions/ADR-001-opencode-v2-baseline.md`
- `../research/compatibility-matrix.md`
