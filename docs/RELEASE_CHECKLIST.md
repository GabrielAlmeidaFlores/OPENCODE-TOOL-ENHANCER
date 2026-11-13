# Release Checklist

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally

Use this checklist before tagging a release. A checked item must have reproducible evidence.

## Repository

- [ ] Working tree clean.
- [ ] `./scripts/validation/validate.sh --links` passes.
- [ ] `make test` passes.
- [ ] [`VERSION`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/VERSION) matches the release tag.
- [ ] `git diff --check` passes.
- [ ] No credentials or machine-specific paths are committed.
- [ ] [`THIRD_PARTY_NOTICES.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/THIRD_PARTY_NOTICES.md) matches the current sources.
- [ ] [`docs/provenance/registry.yml`](provenance/registry.yml) points to existing paths and authors.

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

- [ ] `python3 -m pip wheel ./packages/toolwright_cli --no-deps` builds a wheel.
- [ ] `toolwright --version` matches [`VERSION`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/VERSION).
- [ ] `toolwright doctor --json` exits 0.
- [ ] `toolwright install --apply` into a temporary target writes a lock and state.
- [ ] A second `toolwright install --apply` reports `already up to date`.
- [ ] `toolwright update --check` exits 0, then 1 after a managed file changes.
- [ ] `toolwright uninstall --apply --yes` removes managed files and keeps modified ones.
- [ ] `toolwright rollback` lists backups without writing.

## Profiles and catalog

- [ ] `toolwright profile verify` passes.
- [ ] `toolwright catalog verify` passes.
- [ ] `toolwright catalog verify --check-drift` passes.
- [ ] [`catalog/registry.json`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/catalog/registry.json) and [`catalog/index.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/catalog/index.md) match the provenance registry.
- [ ] `toolwright compat` reflects the pinned OpenCode versions.

## Verification and governance

- [ ] `toolwright verify` passes with the committed [`.toolwright/config.toml`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/.toolwright/config.toml).
- [ ] Failing checks return a non-zero exit and a failure class.
- [ ] `toolwright govern contracts` passes.
- [ ] Governance limits and risk gates match the documented defaults.
- [ ] Ralph `code-assist` finalizer references `toolwright verify`.

## Stats, evals, and pilots

- [ ] `toolwright stats` and `toolwright eval` pass.
- [ ] Pilot dry-run works for all three repositories.
- [ ] No pilot result is published without correctness and rework data.
- [ ] Reporting artifacts contain no credentials.

## Memory and specs

- [ ] Memory and spec commands are covered by tests.
- [ ] [`.toolwright/memory/catalog.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/.toolwright/memory/catalog.md) matches the entries.
- [ ] No credential-shaped text is committed under `.toolwright/memory/`.
- [ ] `specs/` contains no placeholder-only spec marked complete.

## Orchestration




- [ ] `ralph preflight` passes.
- [ ] `ralph run --dry-run` works for each collection.
- [ ] `research` reaches `RESEARCH_COMPLETE` on a small question.
- [ ] `code-assist` reaches completion within the documented iteration budget.
- [ ] `scripts/maintenance/run-ralph-isolated.sh --dry-run` works.
- [ ] No Ralph run writes a commit to the main checkout.

## CI

- [x] GitHub Actions is green on macOS (run 43277080347).
- [x] GitHub Actions is green on Linux (run 43277080347).
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
- [ ] [`CHANGELOG.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/CHANGELOG.md) has an entry for the release.
- [ ] Version follows semantic versioning.
- [ ] Tag and release notes exist.
- [ ] Upgrade and rollback paths are documented.
- [ ] `python3 scripts/release/check_version.py` passes.
- [ ] `mkdocs build --strict` passes.
- [ ] A `v<VERSION>` tag produces a release with the wheel and `SHA256SUMS`.
- [ ] The release workflow verifies the tag against [`VERSION`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/VERSION).
- [ ] The upstream drift workflow is enabled.
- [ ] Upstream pins for OpenCode, Ralph, Serena, and CodeGraph are current or intentionally pinned.
