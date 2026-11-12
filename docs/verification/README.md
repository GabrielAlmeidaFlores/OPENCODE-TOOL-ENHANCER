# Verification Engine

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally; CI runs `ote verify`

`ote verify` runs the repository's deterministic checks from `.ote/config.toml` and treats exit codes as authoritative. It is the gate used by Ralph, CI, and local workflows.

## Configuration

```toml
[verify]
timeout = 900

[verify.checks.validate]
command = "./scripts/validation/validate.sh"
timeout = 120

[verify.checks.test]
command = "python3 -m unittest discover -s tests -t ."
timeout = 900
inputs = ["tests", "packages"]
```

| Field | Meaning |
|---|---|
| `verify.timeout` | Default timeout in seconds |
| `verify.checks.<name>.command` | Shell command, run from the repository root |
| `verify.checks.<name>.timeout` | Per-check timeout, overriding the default |
| `verify.checks.<name>.inputs` | Optional paths used as a cache key |

TOML is used because Python 3.11 provides `tomllib` in the standard library; no runtime dependency is added. See `docs/decisions/ADR-008-toml-verification-config.md`.

## Commands

```bash
ote verify
ote verify --only test
ote verify --only validate --only lint
ote verify --no-cache
ote verify --json
```

Exit codes:

| Code | Meaning |
|---|---|
| 0 | Every selected check passed |
| 1 | At least one check failed |
| 2 | Configuration error, unknown check, or missing input |

## Cache

A check with `inputs` caches a **passing** result under `.ote/cache/verify/<name>.json`. The key covers the command, timeout, and a SHA-256 digest of every declared input file. Editing an input invalidates the entry. Failures are never cached, so a fixed environment is re-tested.

`.ote/cache/` is gitignored.

## Failure classes

| Class | Condition |
|---|---|
| `timeout` | The check exceeded its timeout |
| `missing-command` | Exit 127 |
| `permission` | Exit 126 |
| `test-failure` | Check name contains `test` |
| `lint-failure` | Check name contains `lint` |
| `type-failure` | Check name contains `type` |
| `validation-failure` | Check name contains `validate` |
| `security-failure` | Check name contains `security` |
| `command-failure` | Any other non-zero exit |

The class is reported in text and JSON output and is used by cost and rework reports in later phases.

## JSON output

```json
{
  "results": [
    {
      "name": "test",
      "status": "pass",
      "exit_code": 0,
      "seconds": 20.1,
      "failure_class": "",
      "cached": false,
      "stdout": "",
      "stderr": ""
    }
  ],
  "summary": {
    "total": 1,
    "passed": 1,
    "failed": 0,
    "status": "pass",
    "failure_classes": []
  }
}
```

## Adding a check

1. Add a `[verify.checks.<name>]` table with a command.
2. Add `inputs` only when the check is deterministic and expensive enough to cache.
3. Run `ote verify --only <name>`.
4. Keep the command exit-code based; do not parse model output.

## CI

The `cli` job runs `ote verify --only validate --only lint`, and the Ralph `code-assist` finalizer is instructed to run `ote verify` before completion.

## References

- `docs/governance/README.md`
- `docs/decisions/ADR-008-toml-verification-config.md`
- `docs/architecture/testing.md`
