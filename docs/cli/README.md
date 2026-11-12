# `ote` Command Line

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally on macOS; CI job `cli` defined

`ote` is the single entry point for installing and maintaining the profile. It is a thin
Python layer over the repository's existing shell scripts: it does not reimplement the
installer, the validator, or the backup scripts.

## Install

From a checkout:

```bash
uv tool install ./packages/ote_cli
```

```bash
pipx install ./packages/ote_cli
```

Without installing:

```bash
PYTHONPATH=packages/ote_cli python3 -m ote_cli --help
```

The package requires Python 3.11 or newer and has no runtime dependencies.

## Command status

| Command | Status | Purpose |
|---|---|---|
| `ote doctor` | Available | Repository, dependency, validator, lock, and MCP diagnostics |
| `ote install` | Available | Plan an installation; `--apply` writes it |
| `ote uninstall` | Available | Plan removal; `--apply --yes` removes managed files |
| `ote update --check` | Available | Compare the lock with the current and remote source |
| `ote rollback` | Available | List backups; `--apply --backup DIR --yes` restores one |
| `ote profile` | Available | List, show, verify, and apply profile manifests |
| `ote catalog` | Available | List, search, verify, and build the artifact catalog |
| `ote compat` | Available | OpenCode V1/V2 compatibility matrix |
| `ote verify` | Available | Deterministic verification checks and failure classes |
| `ote govern` | Available | Contracts, budgets, loop/deadlock detection, risk gates |
| `ote memory` | Available | Markdown project memory |
| `ote spec` | Available | Spec-driven development artifacts |
| `ote stats` | Available | Cost, token, failure, and arm comparison reports |
| `ote eval` | Available | Deterministic repository evaluations |
| `ote pilot` | Available | Real-repository pilot runner |
| `ote task` | Experimental | Optional Markdown task board and worktrees |

Unknown commands are rejected by the argument parser with exit code 2.

## `ote profile`

```bash
ote profile list
ote profile show standard
ote profile verify
ote profile use minimal --target ../my-project --apply
```

Profiles are loaded from `profiles/*.yml`. `profile use` delegates to `ote install` and keeps the same
plan/apply, backup, and lock behavior. See `docs/profiles/README.md`.

## `ote catalog`

```bash
ote catalog list
ote catalog list --type agent
ote catalog search security
ote catalog verify
ote catalog verify --check-drift
ote catalog build
```

The catalog is generated from `docs/provenance/registry.yml`. It records the author, source, pinned
commit, license, local path, and modification note for every agent, skill, command, and hat.
`--check-drift` fails when the committed catalog differs from the registry. See
`docs/catalog/README.md`.

`build` and `--check-drift` need PyYAML in the interpreter that runs the generator. Install it for a
`uv` tool with `uv tool install --with pyyaml ./packages/ote_cli`, or for pipx with
`pipx inject ote-cli pyyaml`.

## `ote compat`

```bash
ote compat
ote compat --json
```

Prints the OpenCode V1/V2 matrix. Cells that were not verified are marked `not verified` rather than
guessed. This is a compatibility matrix, not a benchmark. See `docs/agents/compatibility.md` and
`docs/decisions/ADR-001-opencode-v2-baseline.md`.

## `ote verify`

```bash
ote verify
ote verify --only test
ote verify --json
ote verify --no-cache
```

Runs the checks in `.ote/config.toml`, treats exit codes as authoritative, and caches passing results for checks with declared inputs. See `docs/verification/README.md`.

## `ote govern`

```bash
ote govern contracts
ote govern gate --risk high
ote govern check --record run.json
```

Contracts are derived from agent permissions; budgets and limits come from the `[governance]` table. See `docs/governance/README.md`.

## `ote task`

```bash
ote task add "Add rate limiting" --verify "npm test -- rate-limit"
ote task list
ote task move T-001 in-progress
ote task move T-001 done --approved
ote task status
ote task worktree T-001 --remove --yes
```

Markdown board with a WIP limit and one optional Git worktree per task. No merges and no automatic commits. See `.ote/board/README.md`.

## `ote memory`

```bash
ote memory add "Use expand-and-contract migrations" --type constraint --source docs/decisions/ADR-001.md
ote memory search migrations
ote memory prune
ote memory export --format json
ote memory preamble --budget 1500
```

Markdown-only memory with lexical search, TTL, deduplication, and credential rejection. See `docs/memory/README.md`.

## `ote spec`

```bash
ote spec new "Add user authentication" --criterion "A rejected password returns 401"
ote spec list
ote spec plan user-authentication
ote spec verify user-authentication
```

Creates requirements, design, tasks, and evidence artifacts; `plan` and `verify` enforce criterion-to-task-to-evidence mapping. See `docs/specs/README.md`.

## `ote stats`

```bash
ote stats
ote stats --format json
ote stats --format csv
ote stats --results /path/to/results
ote stats --budget 5.00
```

Aggregates `meta.json` and `session.jsonl` artifacts by run, agent, model, and tool. `--budget`
exits 1 when the recorded total exceeds the ceiling. See `docs/cost-optimization/observability.md`.

## `ote eval`

```bash
ote eval
ote eval --only profiles
ote eval --json
```

Runs deterministic checks for profiles, catalog, governance, and the validator. No model calls.
See `docs/evals/README.md`.

## `ote pilot`

```bash
ote pilot list
ote pilot run hono --dry-run
OPENCODE_PILOT_MODEL=provider/model ote pilot run hono --prompt "..." --verify "npm test" --workspace /tmp/pilot
```

Clones a pinned repository into a disposable workspace, installs the profile, runs one prompt, and
records verification, cost, and tokens. See `docs/pilots/README.md`.

## `ote doctor`

```bash
ote doctor
ote doctor --json
ote doctor --no-mcp
```

Checks:

| Check | Fails when |
|---|---|
| `python` | Older than 3.11 |
| `repository` | Required repository files are missing |
| `artifacts` | Any agent, command, skill, or hat count is zero |
| `git` | Git is not installed |
| `opencode` | Missing, unparseable, or V1 |
| `node`, `rg`, `ast-grep`, `serena`, `codegraph`, `ralph` | Missing (warning, not failure) |
| `validator` | `scripts/validation/validate_config.py` fails |
| `lock` | Installed files differ from `ote.lock.json` |
| `state` | `.ote/state.json` is not a directory when present |
| `mcp` | `opencode --standalone mcp list` fails for the target |

Exit code is 0 when no check fails, 1 otherwise. Warnings do not fail the run.

## `ote install`

```bash
ote install --profile standard --target ../my-project --dry-run
ote install --profile standard --target ../my-project --apply
```

Default behavior is a **plan**: it prints every destination path and writes nothing.

| Flag | Effect |
|---|---|
| `--profile minimal` | Config only: opencode, agents, commands, skills, Ralph |
| `--profile standard` | Minimal plus ast-grep |
| `--profile full` | Standard plus Serena and CodeGraph |
| `--only LIST` | Explicit comma-separated components; overrides the profile |
| `--apply` | Execute the plan |
| `--dry-run` | Explicit plan mode; mutually exclusive with `--apply` |
| `--force` | Apply even when the lock says the target is current |
| `--clean` | Back up and replace managed directories before copying |
| `--json` | Machine-readable result |

Apply performs these steps in order:

1. Resolve components and build the file plan.
2. Stop when the lock already matches the source contents, profile, components, and file
   digests (unless `--force`).
3. Archive the target's existing `.opencode` and `.ralph` into `.ote/backups/<timestamp>/`. The global `~/.config/opencode` is never archived.
4. Invoke `scripts/installation/install.sh --apply --only ... --target ...` and print its output.
5. Verify that every planned destination exists.
6. Write `ote.lock.json` and `.ote/state.json`.

Re-running `--apply` without source or target changes reports `already up to date`,
refreshes the recorded source commit, and leaves the managed file digests unchanged.

The lock tracks files only. External tool components (`ast-grep`, `serena`, `codegraph`)
are delegated to the shell installer and are not tracked; use `ote doctor` to verify them.
Tool components can install packages globally, so `--profile minimal` avoids them and the
apply output names every tool step.

## `ote uninstall`

```bash
ote uninstall --target ../my-project
ote uninstall --target ../my-project --apply --yes
ote uninstall --target ../my-project --apply --yes --force --purge
```

Only files recorded in `ote.lock.json` are considered. A file whose digest no longer matches
the lock is preserved and reported, unless `--force` is given. `--purge` also removes the
lock and `.ote` state. Files outside the target are refused even if a lock entry points
there.

## `ote update --check`

```bash
ote update --check
ote update --check --remote --json
```

| Status | Exit code | Meaning |
|---|---|---|
| `current` | 0 | Lock, files, and source commit agree |
| `update-available` | 1 | Source commit or remote HEAD advanced |
| `modified` | 1 | Managed files differ from the lock |
| `unknown` | 1 | Remote head could not be read |
| `no-lock` | 2 | Nothing installed by `ote` |

`--remote` runs `git ls-remote <repository> HEAD`. It does not fetch or modify the local
repository.

## `ote rollback`

```bash
ote rollback --target ../my-project
ote rollback --target ../my-project --apply --backup ../my-project/.ote/backups/20261112T130000Z --yes
```

Backups are created by `scripts/maintenance/backup-config.sh --project-only` and restored
by `scripts/maintenance/restore-config.sh`. The restore overwrites `.opencode` and `.ralph`, so
`--yes` is mandatory.

The shell installer also writes its own `.opencode-backup-<timestamp>` directory. That is
separate from the CLI backup and is not used by `ote rollback`.

## Lock file

`ote.lock.json` is written at the target root and is intended to be committed by the target
project.

```json
{
  "schema_version": 1,
  "created": "2026-11-12T13:00:00+00:00",
  "profile": "minimal",
  "components": ["opencode", "agents", "commands", "skills", "ralph"],
  "source": {
    "repository": "https://github.com/GabrielAlmeidaFlores/OPENCODE-TOOL-ENHANCER",
    "commit": "1753ad5",
    "version": "0.1.0",
    "digest": "…",
    "dirty": "false"
  },
  "files": [
    {
      "path": ".opencode/agents/coordinator.md",
      "source": "agents/coordinator/AGENT.md",
      "component": "agents",
      "sha256": "…"
    }
  ]
}
```

`source.digest` covers the destination path and the source file digest for every planned
file, so an uncommitted edit to an artifact is detected on the next apply.

## Safety

- No command runs `git add`, `git commit`, `git push`, or a destructive Git command.
- Write commands require an explicit `--apply`; destructive ones additionally require `--yes`.
- Removal is limited to lock entries inside the target.
- Backups are created before overwrite.
- The global OpenCode configuration is never modified.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Success, including a no-op plan |
| 1 | Diagnostics failed, or update drift detected |
| 2 | Usage error, missing confirmation, missing lock, or a not-yet-implemented command |

## Design references

The command surface and installer UX were informed by `weisser-dev/awesome-opencode`
(`cli-tool/src/setup.js`, MIT) and `DVNghiem/FlowDeck` (`install.sh`, MIT). The lock and
diff model follows the lockfile idea in `juanmanueldaza/nerv` (Apache-2.0). The
implementation is original Python with no copied code; see
`docs/provenance/registry.yml` entry `ote-cli`.

## References

- `docs/installation/ote-cli.md`
- `docs/architecture/testing.md`
- `docs/troubleshooting/ci.md`
- `docs/decisions/ADR-005-cli-stack.md`
