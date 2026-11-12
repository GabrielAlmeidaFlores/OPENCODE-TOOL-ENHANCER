# Compatibility Policy

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** matrix and CI checks verified locally

## Supported targets

| Target | Supported | Notes |
|---|---|---|
| OpenCode `2.2.x` | Yes | Primary runtime; CI pins `@opencode/cli@2.2.7` |
| OpenCode `1.x` | No | Configuration shape differs; migration only |
| Ralph Orchestrator `2.10.x` | Yes | Auto-commit limitation documented |
| Python | 3.11+ | CLI and validator |
| macOS / Linux | Yes | Windows via WSL or Git Bash |

## Compatibility matrix

```bash
ote compat
ote compat --json
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
| Compatibility matrix | `ote compat` |
| Catalog drift | `ote catalog verify --check-drift` |

## References

- `../agents/compatibility.md`
- `../decisions/ADR-001-opencode-v2-baseline.md`
- `../research/compatibility-matrix.md`
