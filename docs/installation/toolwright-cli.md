# Install the `toolwright` CLI

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally on Python 3.14.7

`toolwright` installs and maintains the profile. It requires Python 3.11 or newer and has no
runtime dependencies.

## Prerequisites

- Python 3.11 or newer.
- One installer: `uv` (recommended) or `pipx`.
- A checkout of this repository, because `toolwright` reads the artifacts from it.

Check the interpreter:

```bash
python3 --version
```

## Install with uv

```bash
git clone https://github.com/GabrielAlmeidaFlores/toolwright.git
cd ToolWright
uv tool install ./packages/toolwright_cli
```

Verify:

```bash
toolwright --version
toolwright doctor
```

`uv tool install` places the `toolwright` script in `~/.local/bin`, which must be on `PATH`.

## Install with pipx

```bash
pipx install ./packages/toolwright_cli
```

## Run without installing

Useful for evaluating the CLI without changing the machine:

```bash
PYTHONPATH=packages/toolwright_cli python3 -m toolwright_cli doctor
PYTHONPATH=packages/toolwright_cli python3 -m toolwright_cli install --profile minimal --target /tmp/demo --dry-run
```

## Upgrade

From a checkout with new changes:

```bash
uv tool install --force ./packages/toolwright_cli
```

`toolwright` reads the artifacts from the repository it is run against, so updating the CLI is only
needed when the CLI code changes. Profile updates are handled by `toolwright install --apply`
after updating the checkout.

## Uninstall

```bash
uv tool uninstall toolwright-cli
```

Do not remove installed project files with `pip`. Use `toolwright uninstall --target <project>
--apply --yes` from the project, then uninstall the tool.

## Verify the installation

```bash
toolwright --version
toolwright doctor --json
```

Expected: exit code 0 and a JSON summary with no failures. Warnings for optional tools such
as Serena or CodeGraph are normal.

## Common problems

| Symptom | Cause | Fix |
|---|---|---|
| `toolwright: command not found` | `~/.local/bin` is not on `PATH` | Export it or reinstall with `pipx` |
| `cannot locate the ToolWright repository` | Running outside a checkout | Run from the checkout or set `TOOLWRIGHT_REPO=/path/to/checkout` |
| `opencode` fails in doctor | OpenCode is missing or is V1 | Install `@opencode/cli` 2.2.x |
| `validator` fails | Repository content is invalid | Run `make validate` and fix the reported item |
| `opencode` fails in doctor | OpenCode is missing or is V1 | The check reports the reason; install `@opencode/cli` 2.2.x |
| `toolwright install` reports `already up to date` but you changed an artifact | Source digest still matches | Use `--force` only when you intend to rewrite files |

## Build a wheel

```bash
python3 -m pip wheel ./packages/toolwright_cli --no-deps --wheel-dir dist
```

The wheel contains the CLI only. It does not contain agents, skills, commands, or configs;
those come from the repository checkout.

The package version is declared twice: `VERSION` for the repository and `[project].version`
in `packages/toolwright_cli/pyproject.toml`. A test fails when they differ, so bump both together.

## References

- `docs/cli/README.md`
- `docs/decisions/ADR-005-cli-stack.md`
- https://docs.astral.sh/uv/
- https://pipx.pypa.io/
