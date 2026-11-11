# Changelog

All notable changes to this repository are documented here.

## [Unreleased]

### Added

- Phase 1 research report with verified compatibility findings.
- Architecture decision records for the OpenCode V2 baseline, Ralph orchestration, maximal code intelligence, and benchmark scope.
- OpenCode V2 project configuration with cost and context controls.
- Custom `coordinator` primary agent and eleven specialized subagents.
- Ralph Orchestrator core configuration and hat collections.
- Code-intelligence guides for ripgrep, ast-grep, Serena, and CodeGraph.
- Code-development skills pack.
- Installation, validation, benchmarking, and maintenance scripts.
- TypeScript and C# examples.
- Benchmark methodology and harness.

### Verified

- OpenCode 2.2.7 keeps `run --agent`, `--model`, `--format json`, and `stats --cost --json`.
- Ralph hats support `backend_args` (alias `args`), enabling per-hat OpenCode agent routing.
- CodeGraph is MIT licensed and exposes `codegraph serve --mcp`.

### End-to-end verification (2026-11-11)

- OpenCode 2.2.7 loaded 19 agents in an isolated project (7 built-in + 12 custom).
- Serena 2.1.0 and CodeGraph 1.6.2 connected over MCP.
- TypeScript example: 7/7 tests pass.
- C# example: 4/4 tests pass.
- Ralph 2.10.1 completed a code-assist loop in 5 iterations with `LOOP_COMPLETE` and `npm test` evidence.

### Fixed during verification

- Ralph event syntax is XML (`<event topic="...">`), not `EVENT: ...`.
- Removed duplicate `default_publishes` from custom hats.
- Replaced `build.done` with `build.ready` to avoid Ralph's backpressure gate.
- Scoped `required_events` to the code-assist collection.
- Allowed transient temp directories so Ralph can pass large prompts.
- Coordinator may run shell commands for verification while remaining edit-denied.

### Known limitations

- OpenCode V2 does not run language servers; Serena replaces native LSP.
- No benchmark results are published; only methodology and harness.
- Ralph's OpenCode backend is plain text, so gates depend on exit codes.
