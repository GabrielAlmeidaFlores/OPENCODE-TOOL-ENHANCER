# Install the `ote` CLI

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally on Python 3.14.7

`ote` installs and maintains the profile. It requires Python 3.11 or newer and has no
runtime dependencies.

## Prerequisites

- Python 3.11 or newer.
- One installer: `uv` (recommended) or `pipx`.
- A checkout of this repository, because `ote` reads the artifacts from it.

Check the interpreter:

```bash
python3 --version
```

## Install with uv

```bash
git clone https://github.com/GabrielAlmeidaFlores/OPENCODE-TOOL-ENHANCER.git
cd OPENCODE-TOOL-ENHANCER
uv tool install ./packages/ote_cli
```

Verify:

```bash
ote --version
ote doctor
```

`uv tool install` places the `ote` script in `~/.local/bin`, which must be on `PATH`.

## Install with pipx

```bash
pipx install ./packages/ote_cli
```

## Run without installing

Useful for evaluating the CLI without changing the machine:

```bash
PYTHONPATH=packages/ote_cli python3 -m ote_cli doctor
PYTHONPATH=packages/ote_cli python3 -m ote_cli install --profile minimal --target /tmp/demo --dry-run
```

## Upgrade

From a checkout with new changes:

```bash
uv tool install --force ./packages/ote_cli
```

`ote` reads the artifacts from the repository it is run against, so updating the CLI is only
needed when the CLI code changes. Profile updates are handled by `ote install --apply`
after updating the checkout.

## Uninstall

```bash
uv tool uninstall ote-cli
```

Do not remove installed project files with `pip`. Use `ote uninstall --target <project>
--apply --yes` from the project, then uninstall the tool.

## Verify the installation

```bash
ote --version
ote doctor --json
```

Expected: exit code 0 and a JSON summary with no failures. Warnings for optional tools such
as Serena or CodeGraph are normal.

## Common problems

| Symptom | Cause | Fix |
|---|---|---|
| `ote: command not found` | `~/.local/bin` is not on `PATH` | Export it or reinstall with `pipx` |
| `cannot locate the OPENCODE-TOOL-ENHANCER repository` | Running outside a checkout | Run from the checkout or set `OTE_REPO=/path/to/checkout` |
| `opencode` fails in doctor | OpenCode is missing or is V1 | Install `@opencode/cli` 2.2.x |
| `validator` fails | Repository content is invalid | Run `make validate` and fix the reported item |
| `opencode` fails in doctor | OpenCode is missing or is V1 | The check reports the reason; install `@opencode/cli` 2.2.x |
| `ote install` reports `already up to date` but you changed an artifact | Source digest still matches | Use `--force` only when you intend to rewrite files |

## Build a wheel

```bash
python3 -m pip wheel ./packages/ote_cli --no-deps --wheel-dir dist
```

The wheel contains the CLI only. It does not contain agents, skills, commands, or configs;
those come from the repository checkout.

The package version is declared twice: `VERSION` for the repository and `[project].version`
in `packages/ote_cli/pyproject.toml`. A test fails when they differ, so bump both together.

## References

- `docs/cli/README.md`
- `docs/decisions/ADR-005-cli-stack.md`
- https://docs.astral.sh/uv/
- https://pipx.pypa.io/
