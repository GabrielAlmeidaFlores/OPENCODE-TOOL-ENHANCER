# CI Diagnosis and Fixes

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified against GitHub Actions logs

This page records real GitHub Actions failures, their root cause, and the fix. It is
maintained so the same failure is not re-diagnosed twice.

## Failure: `harness dry-run` exits with code 2

Observed on run `43101433803`, job `harness dry-run`:

```text
opencode not found
##[error]Process completed with exit code 2.
```

### Root cause

`benchmarks/harness/run.sh` required `opencode` and `python3` before evaluating `--dry-run`.
The `harness` job installs neither, so the job could never pass. The dry-run only needs
Python to read the task definition; it does not execute OpenCode.

### Fix

The OpenCode requirement now applies only to real runs:

```bash
if [[ "$DRY" != "1" ]]; then
  command -v opencode >/dev/null || { echo "opencode not found"; exit 2; }
fi
```

### Regression test

`tests/integration/test_entrypoints.py::BenchmarkHarnessTests::test_every_task_supports_dry_run_without_opencode`
runs every task with a `PATH` that cannot contain OpenCode and asserts exit code 0.

### Verification

```bash
PATH=/usr/bin:/bin python3 -m unittest tests.integration.test_entrypoints -v
```

## Failure: workflow stuck in `queued`

Run `43095734123` remained queued for more than sixteen hours.

### Diagnosis order

```bash
gh run list --limit 10
gh run view <run-id> --log-failed
gh api /repos/<owner>/<repo>/actions/runs?per_page=5 \
  --jq '.workflow_runs[] | {id,status,conclusion,created_at}'
```

Possible causes, in order of likelihood:

1. Runner availability or a platform incident.
2. A concurrency group holding the run behind another job.
3. Repository or organization spending limits.
4. A workflow that waits for a required check that never starts.

### Mitigation applied

- Added an explicit `concurrency` group with `cancel-in-progress: true` so a superseded
  push cannot hold the queue.
- Split the workflow into independent jobs with short timeouts, so one stuck job does not
  block the others.
- Added `timeout-minutes` to every job.

### How to clear a stuck run

```bash
gh run cancel <run-id>
```

Cancelling a queued run is safe: it performs no repository writes. It is not a substitute
for fixing the cause; record the cause here.

## Risk: wrong OpenCode npm package name

Not observed in a run. Verified locally before it could fail in CI. The package name matters:

```text
npm view opencode-ai version   -> 1.19.5
npm view @opencode/cli version -> 2.2.7
```

Installing `opencode-ai` gives V1, which does not understand the V2 `mcp.servers` shape.
The profile job pins `@opencode/cli@2.2.7` so a silent major-version change cannot alter
discovery behaviour.

## Failure: ShellCheck

ShellCheck runs on Linux only, against `scripts/**`. Two common causes:

| Message | Cause | Fix |
|---|---|---|
| `SC2086` | Unquoted expansion | Quote the variable |
| `SC2317` | Unreachable command | Remove dead code or document the branch |

Run locally before pushing:

```bash
shellcheck scripts/**/*.sh benchmarks/harness/*.sh
```

## Failure: validation passes locally but fails in CI

Common causes:

1. **Python version.** CI uses 3.12; a newer local interpreter may accept syntax that 3.12
   rejects.
2. **PyYAML present locally but not in CI, or the reverse.** The validator falls back to
   Ruby. Install PyYAML in CI explicitly.
3. **Line endings.** A CRLF checkout changes file hashes and shell parsing.
4. **Case-sensitive filesystem.** Linux treats `Agent.md` and `agent.md` as different.
5. **Uncommitted files.** CI runs the commit, not the working tree.

## Risk: managed service port conflict

`opencode debug agents` talks to the managed background service by default. In a fresh
`HOME` the service is started on demand; if another service already holds the chosen port,
the command fails with `Managed service port ... is already in use`.

CI and the test suite use `opencode --standalone debug agents`, which starts a private
server for the command and avoids the shared-service port entirely. Use the same flag when
reproducing discovery in a temporary `HOME`:

```bash
HOME="$(mktemp -d)" OPENCODE_CONFIG="/abs/path/.opencode/opencode.jsonc" \
  opencode --standalone debug agents
```

## Confirmed green

Run [`43234273370`](https://github.com/GabrielAlmeidaFlores/OPENCODE-TOOL-ENHANCER/actions/runs/43234273370)
completed on 2026-11-12 with every job successful:

| Job | Result |
|---|---|
| `static (ubuntu-latest)` | success |
| `static (macos-latest)` | success |
| `test (ubuntu-latest)` | success |
| `test (macos-latest)` | success |
| `examples` | success |
| `cli` | success |
| `opencode profile` | success |
| `harness dry-run` | success |

This confirms the harness fix, the offline suite on both operating systems without a local
OpenCode binary, the CLI wheel build and install lifecycle, OpenCode agent discovery with a
pinned version, and benchmark dry-runs. Action majors are `checkout@v7`, `setup-python@v7`,
`setup-node@v7`, and `setup-dotnet@v6`.

## Job map

| Job | Purpose | Needs |
|---|---|---|
| `static` | Validator, shell syntax, ShellCheck | Python, PyYAML |
| `test` | Unit and integration suites | Python, PyYAML |
| `examples` | TypeScript and C# builds | Node, .NET |
| `opencode-profile` | Install profile and verify discovery | Node, OpenCode V2 |
| `harness` | Benchmark dry-run for every task | Python |
| `cli` | Builds the wheel, runs `ote doctor`, exercises install, update, and uninstall | Python, Node, OpenCode V2 |

## References

- `.github/workflows/validate.yml`
- `docs/architecture/testing.md`
- `docs/validation-checklist.md`
