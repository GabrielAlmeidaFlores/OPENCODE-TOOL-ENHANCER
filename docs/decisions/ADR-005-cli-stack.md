# ADR-005: Implement the repository CLI in Python

- Status: Accepted
- Accepted: 2026-11-12
- Date: 2026-11-12

## Context

The repository exposes its functionality through shell and Python scripts under
`scripts/`. That works for the current workflow but has three problems:

1. Discovery: users must read the README to find the right script.
2. Composition: each script parses its own arguments and duplicates flag handling.
3. Distribution: there is no versioned entry point, so upgrades are manual.

Phase 2 introduces `ote` as a single command surface. The implementation language must be
chosen before the first line of CLI code is written, because the choice affects packaging,
test strategy, and contributor requirements.

Candidates:

| Option | Strengths | Weaknesses |
|---|---|---|
| Python | Validator is already Python; stdlib `argparse`, `json`, `pathlib`; `uv` available | Slower cold start; packaging requires `pyproject.toml` |
| TypeScript/Node | Best ecosystem match for OpenCode plugins; `npm` distribution | Adds a second runtime and a build step; duplicates the validator |
| Shell | No dependency | Poor structure, weak testing, no portable packaging |

## Decision

Implement `ote` in **Python 3.11+** as a package under `packages/ote_cli`, distributed
through `uv tool install` and `pipx`, with `pyproject.toml` as the build definition.

The existing Python validator becomes a module imported by the CLI rather than a
subprocess call. Shell scripts remain supported as thin wrappers so current documentation
and CI keep working unchanged.

## Rationale

- The validation logic already exists in Python and is the most complex part of the
  current tooling. Reusing it avoids a rewrite and keeps one implementation.
- `argparse`, `json`, `pathlib`, `hashlib`, and `urllib` cover the planned command surface
  without third-party runtime dependencies.
- A zero-dependency core keeps CI fast and removes supply-chain surface.
- Contributors already need Python for validation, so no new prerequisite is introduced.

## Consequences

- `pyproject.toml` becomes required and must declare the `ote` console script.
- Unit tests target the modules directly, not shell subprocesses.
- The TypeScript ecosystem is still used for examples and optional OpenCode plugins, but
  not for the CLI.
- Cold start is acceptable for a developer tool; commands that reimplement validation
  must stay under one second on the reference host.

## Alternatives rejected

- **TypeScript CLI:** would require porting the validator and maintaining two
  implementations of the same rules.
- **Shell-only CLI:** argument parsing and JSON output become fragile, and Windows support
  degrades.

## Verification

- `packages/ote_cli/pyproject.toml` builds a wheel and installs the `ote` console script.
- `ote doctor` runs the existing validator as a subprocess and reports its `checked:` count.
- `pyproject.toml` declares no runtime dependencies; the tests assert this.
- `ote install` wraps `scripts/installation/install.sh` instead of reimplementing it.
- 30 unit tests and 13 integration tests cover the command surface.
- The `cli` CI job is defined to install the wheel, run `ote doctor`, and exercise the install lifecycle; its first green run is recorded in `docs/troubleshooting/ci.md` after the next push.

## References

- `docs/research/baseline.md`
- `scripts/validation/validate_config.py`
- https://docs.astral.sh/uv/
