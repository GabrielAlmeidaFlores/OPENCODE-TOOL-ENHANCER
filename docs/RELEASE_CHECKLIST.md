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

## Orchestration

- [ ] `ralph preflight` passes.
- [ ] `ralph run --dry-run` works for each collection.
- [ ] `research` reaches `RESEARCH_COMPLETE` on a small question.
- [ ] `code-assist` reaches completion within the documented iteration budget.
- [ ] `scripts/maintenance/run-ralph-isolated.sh --dry-run` works.
- [ ] No Ralph run writes a commit to the main checkout.

## CI

- [ ] GitHub Actions is green on macOS.
- [ ] GitHub Actions is green on Linux.
- [ ] Shellcheck passes.
- [ ] The OpenCode profile job discovers all twelve agents.
- [ ] Harness dry-runs pass for every task.

## Evidence

- [ ] Benchmark results exist, or the README explicitly marks benchmarks as deferred.
- [ ] Any cost or token claim links to a committed result.
- [ ] Real-repository pilots are complete, or the README marks them as pending.
- [ ] Known limitations and unsupported cases are documented.
- [ ] No vendor benchmark is presented as an independent result.

## Release

- [ ] `CHANGELOG.md` has an entry for the release.
- [ ] Version follows semantic versioning.
- [ ] Tag and release notes exist.
- [ ] Upgrade and rollback paths are documented.
- [ ] Upstream pins for OpenCode, Ralph, Serena, and CodeGraph are current or intentionally pinned.
