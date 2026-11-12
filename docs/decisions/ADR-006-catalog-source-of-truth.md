# ADR-006: Make the provenance registry the single source of truth for the catalog

- Status: Proposed
- Date: 2026-11-12

## Context

Provenance data currently lives in three places:

1. Frontmatter and header comments inside each artifact.
2. `docs/provenance/registry.yml`.
3. Narrative statements in `docs/`.

Phase 3 introduces a consumer-facing catalog (`catalog/*.yaml` plus a generated
`catalog/registry.yml`) so that users and tooling can list, search, and verify artifacts.
If the catalog is maintained by hand it will drift from the provenance registry, and a
drift between two sources of truth is worse than having one incomplete source.

The reference implementation `awesome-opencode` keeps a YAML catalog validated against a
JSON Schema and generates its README from that data. `OpenAgentsControl` keeps a
`registry.json` with `schema_version`, `categories`, `components`, and `profiles`.

## Decision

Keep `docs/provenance/registry.yml` as the **only hand-edited source** and generate
`catalog/*.yaml`, `catalog/registry.yml`, and the documentation tables from it.

Validation runs in this order:

1. JSON Schema validation of the generated catalog.
2. Provenance completeness and commit reachability checks.
3. Drift check: regenerate into a temporary directory and fail if the result differs from
   the committed files.

## Rationale

- One editable file keeps review small.
- Generated files can be replaced without review conflicts.
- The schema check catches structural mistakes; the drift check catches manual edits.
- The same model lets future `ote catalog verify` report a single, unambiguous status.

## Consequences

- `catalog/` is generated output. A pull request that edits it directly fails CI.
- New artifact fields must be added to the generator and the schema together.
- The registry schema becomes a public contract, so it needs `schema_version`.
- Until Phase 3 lands, `docs/provenance/registry.yml` stays hand-maintained and the
  existing validator continues to enforce it.

## Fields required per artifact

| Field | Purpose |
|---|---|
| `id` | Stable identifier used by commands |
| `type` | `agent`, `skill`, `command`, `hat`, `mcp`, `plugin` |
| `author`, `author_url` | Attribution required by AGENTS.md Section 2A |
| `source`, `upstream_path`, `upstream_commit` | Reproducible upstream pin |
| `license` | Distribution constraint |
| `local` | Installed path |
| `modified` | Minimal-diff description |
| `retrieved` | Retrieval date |
| `opencode_compat` | Supported OpenCode versions |
| `smoke_status`, `last_verified` | Verification state |

## Verification required before acceptance

- Deleting a provenance entry makes `ote catalog verify` fail.
- Editing a generated catalog file makes CI fail.
- Regeneration on a clean checkout produces no diff.

## References

- `docs/provenance/registry.yml`
- `docs/provenance/README.md`
- `docs/decisions/ADR-005-cli-stack.md`
