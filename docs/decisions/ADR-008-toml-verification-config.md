# ADR-008: Use TOML for the verification configuration

- Status: Accepted
- Accepted: 2026-11-12
- Date: 2026-11-12

## Context

The implementation plan proposed `.toolwright/config.yml` with a `verify:` table and a `governance:` table. That shape requires nested mappings and lists of tables.

The CLI has a strict zero-runtime-dependency policy. The profile loader supports only a restricted YAML subset (top-level keys and lists), which cannot represent nested verification and governance tables. Adding PyYAML as a runtime dependency would break the policy; writing a general YAML parser would add a large, risky surface for configuration that is machine-authored.

Python 3.11 provides `tomllib` in the standard library. TOML supports tables, nested tables, numbers, arrays, and strings with no dependency.

## Decision

Use `.toolwright/config.toml` with this shape:

```toml
[verify]
timeout = 900

[verify.checks.test]
command = "python3 -m unittest discover -s tests -t ."
inputs = ["tests", "packages"]

[governance]
max_iterations = 40
```

`tomllib` parses the file; the CLI validates types, names, timeouts, and input paths.

## Rationale

- Standard-library parsing keeps `toolwright` dependency-free.
- Nested tables are the right model for per-check settings and governance limits.
- TOML has no comments requirement conflict: the repository prohibits field-level configuration comments, and TOML comments are simply not used.
- Validation errors are deterministic and can point at the exact table.

## Consequences

- The plan's YAML filename is superseded; documentation and scripts use `.toolwright/config.toml`.
- Profiles remain YAML because they are flat and read by the restricted loader.
- The configuration is not editable with YAML tooling; `tomllib` and common editors support TOML.
- `toolwright verify` works without any optional dependency, unlike catalog generation.

## Verification

- `toolwright verify --only lint` runs from the repository with no third-party packages.
- Invalid TOML, missing tables, unknown check names, and missing cache inputs produce exit code 2 with a specific message.
- Unit tests cover loading, validation, execution, classification, and caching.

## References

- `docs/verification/README.md`
- `docs/governance/README.md`
- https://docs.python.org/3/library/tomllib.html
