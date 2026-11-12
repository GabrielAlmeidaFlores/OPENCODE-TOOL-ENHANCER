# Release Checklist

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally

Use this checklist before tagging a release. A checked item must have reproducible evidence.

## Repository

- [ ] Working tree clean.
- [ ] `./scripts/validation/validate.sh --links` passes.
- [ ] `make test` passes.
- [ ] `VERSION` matches the release tag.
- [ ] `git diff --check` passes.
- [ ] No credentials or machine-specific paths are committed.
- [ ] `THIRD_PARTY_NOTICES.md` matches the current sources.
- [ ] `docs/provenance/registry.yml` points to existing paths and authors.

## Configuration

- [ ] `opencode debug config` loads the project configuration.
- [ ] `opencode debug agents` lists the coordinator and eleven subagents.
- [ ] `opencode mcp list` shows the intended servers connected or disabled.
- [ ] Git write commands resolve to `deny` for every agent.
- [ ] The minimal profile loads without MCP servers.

## Examples

- [ ] TypeScript example: `npm install && npm test`.
- [ ] C# example: `dotnet test Example.Tests/Example.Tests.csproj`.
- [ ] Installer applies to a temporary project and reports the expected counts.
- [ ] Installer `--clean` removes only selected components and preserves `.ralph/agent`.

## CLI

- [ ] `python3 -m pip wheel ./packages/ote_cli --no-deps` builds a wheel.
- [ ] `ote --version` matches `VERSION`.
- [ ] `ote doctor --json` exits 0.
- [ ] `ote install --apply` into a temporary target writes a lock and state.
- [ ] A second `ote install --apply` reports `already up to date`.
- [ ] `ote update --check` exits 0, then 1 after a managed file changes.
- [ ] `ote uninstall --apply --yes` removes managed files and keeps modified ones.
- [ ] `ote rollback` lists backups without writing.

## Profiles and catalog

- [ ] `ote profile verify` passes.
- [ ] `ote catalog verify` passes.
- [ ] `ote catalog verify --check-drift` passes.
- [ ] `catalog/registry.json` and `catalog/index.md` match the provenance registry.
- [ ] `ote compat` reflects the pinned OpenCode versions.

## Verification and governance

- [ ] `ote verify` passes with the committed `.ote/config.toml`.
- [ ] Failing checks return a non-zero exit and a failure class.
- [ ] `ote govern contracts` passes.
- [ ] Governance limits and risk gates match the documented defaults.
- [ ] Ralph `code-assist` finalizer references `ote verify`.

## Stats, evals, and pilots

- [ ] `ote stats` and `ote eval` pass.
- [ ] Pilot dry-run works for all three repositories.
- [ ] No pilot result is published without correctness and rework data.
- [ ] Reporting artifacts contain no credentials.

## Memory and specs

- [ ] Memory and spec commands are covered by tests.
- [ ] `.ote/memory/catalog.md` matches the entries.
- [ ] No credential-shaped text is committed under `.ote/memory/`.
- [ ] `specs/` contains no placeholder-only spec marked complete.

## Orchestration




- [ ] `ralph preflight` passes.
- [ ] `ralph run --dry-run` works for each collection.
- [ ] `research` reaches `RESEARCH_COMPLETE` on a small question.
- [ ] `code-assist` reaches completion within the documented iteration budget.
- [ ] `scripts/maintenance/run-ralph-isolated.sh --dry-run` works.
- [ ] No Ralph run writes a commit to the main checkout.

## CI

- [x] GitHub Actions is green on macOS (run 43275405166).
- [x] GitHub Actions is green on Linux (run 43275405166).
- [x] ShellCheck passes on Linux.
- [x] The OpenCode profile job discovers all twelve agents.
- [x] Harness dry-runs pass for every task.

## Evidence

- [ ] Benchmark results exist, or the README explicitly marks benchmarks as deferred.
- [ ] Any cost or token claim links to a committed result.
- [ ] Real-repository pilots are complete, or the README marks them as pending.
- [ ] Known limitations and unsupported cases are documented.
- [ ] No vendor benchmark is presented as an independent result.

## Task board and plugin

- [ ] Task board state is reviewable in Git; worktrees are gitignored.
- [ ] No task is marked done without approval.
- [ ] The memory plugin is opt-in and absent from default profiles.
- [ ] Plugin file syntax passes `node --check`.

## Release
- [ ] `CHANGELOG.md` has an entry for the release.
- [ ] Version follows semantic versioning.
- [ ] Tag and release notes exist.
- [ ] Upgrade and rollback paths are documented.
- [ ] `python3 scripts/release/check_version.py` passes.
- [ ] `mkdocs build --strict` passes.
- [ ] A `v<VERSION>` tag produces a release with the wheel and `SHA256SUMS`.
- [ ] The release workflow verifies the tag against `VERSION`.
- [ ] The upstream drift workflow is enabled.
- [ ] Upstream pins for OpenCode, Ralph, Serena, and CodeGraph are current or intentionally pinned.
