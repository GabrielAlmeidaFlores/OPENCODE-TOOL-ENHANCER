# Baseline Record

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally on macOS 26.5.2

This page records the environment, versions, and validation output at the start of the
operationalization work. Every later cost, compatibility, or performance claim compares
against this record.

## Purpose

The repository previously had no frozen baseline. Without one, later phases cannot
distinguish a regression from a pre-existing condition, and benchmark results cannot be
reproduced. This record fixes the reference point.

## Reference commit

```text
b4af8e8b7005462da8daa233c82652499e6f7d8e
docs: record runtime smoke tests and cost observability
Wed Nov 11 18:15:05 2026 -0300
```

## Local environment

| Component | Version | Notes |
|---|---|---|
| macOS | 26.5.2 (build 25F84) | Primary development host, Apple Silicon |
| Git | 2.56.0 | |
| Python | 3.14.7 | Validator requires 3.11 or newer |
| Node.js | 24.18.0 | Used by examples and OpenCode distribution |
| uv | 0.13.7 | Candidate installer for the Phase 2 CLI |
| ShellCheck | 0.11.0 | Shell syntax and lint gate |
| OpenCode | 2.2.7 | V2 baseline, see [`docs/decisions/ADR-001-opencode-v2-baseline.md`](../decisions/ADR-001-opencode-v2-baseline.md) |

Package availability observed on 2026-11-12:

```text
npm view opencode-ai version   -> 1.19.5
npm view @opencode/cli version -> 2.2.7
```

The V2 package is `@opencode/cli`. The name `opencode-ai` still resolves to the V1
release line, so CI and installation instructions must use `@opencode/cli`.

## Validation output

Command:

```bash
./scripts/validation/validate.sh
```

Observed output:

```text
== files ==
== jsonc / yaml / frontmatter ==
checked: 142
OK
== opencode ==
opencode v2.2.7
debug agents: ok
== shell syntax ==
OK
```

Classification: local execution, deterministic, reproducible without network access.

## OpenCode configuration sources

```bash
opencode debug paths
opencode debug config
```

`debug paths` confirms the V2 directory layout: `config` under `~/.config/opencode`,
`data` under `~/.local/share/opencode`, and `state` under `~/.local/state/opencode`.
The project configuration is validated separately by the validator.

## Known gaps at baseline

| Gap | Consequence | Addressed in |
|---|---|---|
| CI had a failed run for `harness dry-run` | No reliable remote signal | Phase 1 |
| No unit tests for `validate_config.py` | Regressions reach `main` | Phase 1 |
| No integration tests for commands and skills | Manual smoke only | Phase 1 |
| No [`VERSION`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/VERSION) file | No versioned release or update check | Phase 0 |
| No status metadata on docs | Readers cannot tell stable from planned | Phase 0 |
| Validator knows nothing about [`VERSION`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/VERSION) | Required-file check is incomplete | Phase 1 |

## Evidence classification used in this document

| Label | Meaning |
|---|---|
| Verified locally | Run on the reference host and observed directly |
| Verified in CI | Reproduced by a GitHub Actions job |
| Vendor claim | Published by a maintainer without independent reproduction |
| Unverified | Stated as a hypothesis, not a result |

Only the first two labels may appear in a claim of correctness or cost.

## Reproduction

```bash
git switch --detach b4af8e8b7005462da8daa233c82652499e6f7d8e
./scripts/validation/validate.sh
```

## References

- [`docs/validation-checklist.md`](../validation-checklist.md)
- [`docs/decisions/ADR-001-opencode-v2-baseline.md`](../decisions/ADR-001-opencode-v2-baseline.md)
- [`docs/troubleshooting/ci.md`](../troubleshooting/ci.md)
