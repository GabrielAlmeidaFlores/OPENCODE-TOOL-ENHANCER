# Profiles

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally and in CI run 43239159927

Profiles are declarative manifests under `profiles/`. They replace the provisional component lists that were embedded in the CLI.

## Available profiles

| Profile | Contents | Use when |
|---|---|---|
| `minimal` | OpenCode config, agents, commands, skills, Ralph | You want no global tool installation |
| `standard` | Minimal plus `ast-grep` | Default; structural search is useful |
| `full` | Standard plus Serena, CodeGraph, and the opt-in memory plugin | You want symbol navigation and dependency graphs |

Tool components may install packages globally. `standard` and `full` print the tool step, and `minimal` avoids it.

## Commands

```bash
toolwright profile list
toolwright profile show standard
toolwright profile verify
toolwright profile use minimal --target ../my-project --dry-run
toolwright profile use minimal --target ../my-project --apply
```

`profile use` delegates to `toolwright install` with the manifest's components; all install safeguards apply.

## Manifest format

The loader supports a restricted YAML subset: top-level scalar keys and lists of strings. This keeps the CLI free of a YAML runtime dependency.

```yaml
# Name: Example profile
# Purpose: Demonstrates the manifest format.
# Usage: toolwright install --profile example
# Validation: toolwright profile verify
# References: docs/profiles/README.md

name: example
description: Short description shown by toolwright profile list.
components:
  - opencode
  - agents
```

Rules enforced by `toolwright profile verify`:

- the file name must equal `name`;
- `description` is required;
- `components` is a non-empty list;
- components must be one of `opencode`, `agents`, `commands`, `skills`, `ralph`, `plugin`, `ast-grep`, `serena`, `codegraph`;
- duplicate components are rejected;
- nested mappings and block scalars are rejected.

## Adding a profile

1. Create `profiles/<name>.yml` using the format above.
2. Run `toolwright profile verify`.
3. Run `toolwright profile use <name> --target /tmp/check --dry-run`.
4. Document the profile in this table.

## Design reference

The profile concept follows the selection model in `weisser-dev/awesome-opencode` (`cli-tool/src/setup.js`, MIT) and the `profiles` section of `OpenAgentsControl`'s registry (MIT). The manifest loader is original Python; see the `catalog-and-profiles` entry in `docs/provenance/registry.yml`.

## References

- `docs/catalog/README.md`
- `docs/cli/README.md`
- `docs/validation-checklist.md`
