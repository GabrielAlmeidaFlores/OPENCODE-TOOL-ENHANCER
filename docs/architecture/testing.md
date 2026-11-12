# Testing the Repository

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally

This page describes how the repository tests its own tooling. It does not describe how
to test a user project; see the `test-engineer` agent and the `test-driven-development`
skill for that.

## Why the repository needs tests

The repository ships scripts, configuration, and agent definitions. A broken validator or
installer is a broken product, even when no application code changes. Before Phase 1 the
only automated check was the validator itself, which had no tests, and command and skill
smoke checks were performed manually.

## Test layers

| Layer | Location | Runs in CI | Needs network | Needs a model |
|---|---|---|---|---|
| Unit | `tests/unit/` | Yes | No | No |
| Integration | `tests/integration/` | Yes | No | No |
| Runtime discovery | `tests/integration/test_opencode_runtime.py` | Yes, when OpenCode is installed | No | No |
| CLI lifecycle | `tests/integration/test_ote_commands.py` | Yes, in the `cli` job | No | No |
| Benchmark execution | `benchmarks/harness/` | Dry-run only | No | Yes, for real runs |

## Running the suite

```bash
# Everything
make test

# One module
python3 -m unittest tests.unit.test_validate_config -v

# One test
python3 -m unittest tests.unit.test_validate_config.AgentChecksTests.test_valid_agent_passes -v
```

The suite uses the Python standard library `unittest` runner. This is deliberate: the
repository already requires Python for validation, and a zero-dependency test runner keeps
CI fast and removes a supply-chain surface. `make test` therefore works on a clean machine
with no virtual environment.

CI additionally installs PyYAML so the YAML checks run against a real parser instead of the
Ruby fallback.

## How the validator is tested

`tests/support.py` imports `scripts/validation/validate_config.py` as a module, points its
`ROOT` at a temporary directory, resets its counters, and runs one check at a time.

```python
validator = support.load_validator()
with support.isolated_root(validator) as root:
    support.write_file(root, "agents/coordinator/AGENT.md", fixture)
    validator.check_agents()
    assert validator.errors == []
```

This keeps tests fast and prevents them from depending on the real repository layout, so a
fixture can exercise one rule without satisfying the other eleven roles.

## Fixtures

`tests/fixtures/` contains deliberately broken artifacts:

| Fixture | Rule exercised |
|---|---|
| `agents/missing-description.md` | Agent description is required |
| `agents/wrong-mode.md` | Coordinator must be `primary` |
| `agents/missing-provenance.md` | Section 2A attribution headers |
| `agents/git-allow-last.md` | Last matching permission wins |
| `commands/missing-agent.md` | Commands must name an agent |
| `commands/unknown-agent.md` | Commands must name a known agent |
| `skills/name-mismatch/SKILL.md` | Skill name equals directory |
| `config/commented-body.jsonc` | Section 2C inline-comment rule |
| `config/missing-servers.jsonc` | V2 `mcp.servers` requirement |
| `config/invalid.yml` | YAML parse errors |
| `tasks/missing-field.json` | Required benchmark task fields |
| `tasks/missing-workdir.json` | Task working directory exists |

Fixtures are test inputs only. They are not reusable agents, skills, or commands and must
never be installed.

## What the integration tests assert

- `scripts/validation/validate.sh` exits zero on the repository.
- The comment policy scans `scripts/`, `packages/`, `skills/`, and `tests/`, plus TypeScript and C# sources; Python docstrings must use block form with the quotes on their own lines. Only `tests/fixtures/` is exempt because those files must contain prohibited patterns.
- `validate_config.py` exits zero and prints a `checked:` count.
- Every benchmark task dry-runs without an OpenCode binary and without a model.
- The installer defaults to check-only and creates no files.
- OpenCode discovers all twelve agents when the profile is installed into a temporary
  target, and the coordinator is `primary`.
- The CLI plans without writing, applies into a temporary target, re-applies without
  changing the lock, detects tampered files, refuses destructive commands without
  confirmation, and removes only unmodified managed files.

The OpenCode checks skip cleanly when `opencode` is not on `PATH`, so contributors without
the binary still get a green suite.

## Adding a test

1. Decide the layer. Rules about repository content belong in `tests/unit/`; behaviour of
   an executable entry point belongs in `tests/integration/`.
2. Add a fixture only when the broken input is not expressible with a builder from
   `tests/support.py`.
3. Name the test after the rule, not the implementation. `test_coordinator_requires_primary_mode`
   is useful; `test_check_agents_2` is not.
4. Keep the test independent of the working tree. Use `support.isolated_root`.
5. Run `make test` and `make validate` before returning the change unstaged.

## CI parity

`make test` and CI run the same command. CI adds:

- the OS matrix (`ubuntu-latest`, `macos-latest`) for the static and test jobs;
- ShellCheck on Linux;
- example builds (TypeScript and C#);
- OpenCode profile installation and discovery;
- benchmark dry-run for every task;
- the `cli` job: wheel build, `ote doctor`, and the install/update/uninstall lifecycle.

Paid model calls are excluded from the default workflow. Real benchmark runs are explicit
and require `OPENCODE_BENCH_MODEL`.

## References

- `AGENTS.md` Section 12
- `docs/validation-checklist.md`
- `docs/troubleshooting/ci.md`
- `docs/research/baseline.md`
