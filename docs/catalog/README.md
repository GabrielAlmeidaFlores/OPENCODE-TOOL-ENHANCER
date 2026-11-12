# Verified Artifact Catalog

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally and in CI run 43239159927

The catalog turns the provenance registry into a validated, searchable artifact list. It is generated, never hand-edited.

## Files

| Path | Purpose |
|---|---|
| `catalog/registry.json` | Machine-readable catalog read by `ote` |
| `catalog/index.md` | Human-readable table |
| `catalog/schema/entry.schema.json` | Document and entry schema |
| `scripts/catalog/build_catalog.py` | Generator (build-time only) |

## Commands

```bash
ote catalog list
ote catalog list --type skill
ote catalog search security
ote catalog verify
ote catalog verify --check-drift
ote catalog build
```

`list`, `search`, and `verify` read the committed JSON and need no third-party dependency. `build` and `--check-drift` run the generator, which requires PyYAML because the source is YAML.

```bash
python3 -m pip install pyyaml
python3 scripts/catalog/build_catalog.py
python3 scripts/catalog/build_catalog.py --check
```

Installed CLI environments need the dependency in the same interpreter:

```bash
uv tool install --with pyyaml ./packages/ote_cli
pipx inject ote-cli pyyaml
```

## Schema

Each artifact requires:

| Field | Meaning |
|---|---|
| `id` | Stable identifier |
| `type` | `agent`, `skill`, `command`, or `hat` |
| `section` | Registry section the entry came from |
| `local` | Repository path that must exist |
| `source` | Source identifier from the registry |
| `upstream_path` | Exact upstream path |
| `upstream_commit` | Pinned commit |
| `license` | Upstream license |
| `author`, `author_url` | Attribution required by AGENTS.md Section 2A |
| `retrieved` | Retrieval date |
| `modified` | Minimal-diff description |

`ote catalog verify` checks required fields, the allowed type set, duplicate identifiers, declared counts, and that every local path exists. `--check-drift` additionally regenerates in memory and fails when the committed files differ.

## Adding an artifact

1. Add or update the entry in `docs/provenance/registry.yml`.
2. Run `python3 scripts/catalog/build_catalog.py`.
3. Run `ote catalog verify --check-drift`.
4. Commit the registry change and both generated files together.

A pull request that edits `catalog/registry.json` or `catalog/index.md` without the registry change fails the drift check.

## Design reference

The schema-first approach follows `awesome-opencode` (`data/schema.json`, CC0-1.0) and the `registry.json` structure in `OpenAgentsControl` (MIT). The implementation is original Python; see the `catalog-and-profiles` entry in `docs/provenance/registry.yml`.

## References

- `docs/provenance/registry.yml`
- `docs/profiles/README.md`
- `docs/cli/README.md`
