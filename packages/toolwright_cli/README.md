# toolwright-cli

Command-line interface for ToolWright.

This package wraps the repository's existing installer, validator, backup, and
restore scripts. It does not reimplement them, and it never stages or commits Git
changes.

## Install from a checkout

```bash
uv tool install ./packages/toolwright_cli
# or
pipx install ./packages/toolwright_cli
```

For development without installing:

```bash
PYTHONPATH=packages/toolwright_cli python3 -m toolwright_cli --help
```

## Commands

| Command | Purpose |
|---|---|
| `toolwright doctor` | Repository, dependency, validator, lock, and MCP diagnostics |
| `toolwright install` | Plan an installation; `--apply` writes it |
| `toolwright uninstall` | Plan removal; `--apply --yes` removes managed files |
| `toolwright update --check` | Compare the lock with the current source and optionally the remote |
| `toolwright rollback` | List backups; `--apply --backup DIR --yes` restores one |

Commands planned for later phases are registered and exit with code 2 with a
phase reference instead of pretending to work.

## Guarantees

- Default mode never writes files.
- `--apply` creates a backup before overwriting an existing `.opencode` or `.ralph`.
- The lock records the source commit, profile, components, and a SHA-256 digest per file.
- Uninstall refuses to remove files that changed after installation unless `--force` is given.
- No command runs `git add`, `git commit`, `git push`, or any destructive Git command.

## Documentation

See `docs/cli/README.md` in the repository for the full command reference.

## License

MIT. See the repository `LICENSE` and `THIRD_PARTY_NOTICES.md`.
