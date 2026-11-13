# Compatibility Policy

> **Status:** Stable · **Last verified:** 2026-11-13 · **Evidence:** matrix and CI checks verified locally

## Supported targets

| Target | Level | Notes |
|---|---|---|
| OpenCode `2.2.x` | Native | Reference runtime; CI pins `@opencode/cli@2.2.7` |
| OpenCode `1.x` | No | Configuration shape differs; migration only |
| Ralph Orchestrator `2.10.x` | Native (OpenCode backend) | Auto-commit limitation documented |
| GitHub Copilot | Portable instructions | Documented mapping; not runtime-tested in CI |
| Claude Code | Portable agents and instructions | Documented mapping; not runtime-tested in CI |
| OpenAI GPT / Codex | Portable instructions and custom agents | Documented mapping; not runtime-tested in CI |
| Python | 3.11+ | CLI and validator |
| macOS / Linux | Yes | Windows via WSL or Git Bash |

Native means ToolWright ships the runtime configuration and verifies it. Portable means the same roles and rules are mapped onto the platform's documented file formats; no runtime claim is made.

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
| Catalog drift | `toolwright catalog verify --check-drift` |

## References

- `../agents/compatibility.md`
- `README.md`
- `github-copilot.md`
- `claude.md`
- `openai-gpt.md`
- `../decisions/ADR-001-opencode-v2-baseline.md`
- `../research/compatibility-matrix.md`
