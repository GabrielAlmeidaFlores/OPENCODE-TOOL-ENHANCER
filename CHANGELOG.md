# Changelog

All notable changes to this repository are documented here.

## [Unreleased]

### Added

- `VERSION` file for release and update checks.
- Phase 0 baseline record with frozen environment, versions, and validation output.
- ADR-005 for the Python CLI stack, ADR-006 for a single catalog source of truth, and ADR-007 for Markdown memory without a vector store.
- Status metadata on every documentation page: status, last verified date, and evidence class.
- Unit and integration test suite under `tests/` using the standard library runner.
- Test fixtures that exercise provenance, permissions, JSONC, YAML, skills, commands, and benchmark tasks.
- `Makefile` targets `test`, `lint`, and `ci`.
- Testing guide and CI diagnosis guide.
- Validator check for workflow YAML and documentation status metadata.
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

- CI run `43227605747` is green on Ubuntu and macOS across all seven job instances (static, test, examples, profile discovery, harness dry-run).
- OpenCode 2.2.7 keeps `run --agent`, `--model`, `--format json`, and `stats --cost --json`.
- Ralph hats support `backend_args` (alias `args`), enabling per-hat OpenCode agent routing.
- CodeGraph is MIT licensed and exposes `codegraph serve --mcp`.

### Fixed

- Benchmark harness dry-run no longer requires the OpenCode binary; the CI `harness` job failed with exit code 2 because OpenCode was never installed there. Dry-run now validates task inputs only, and real runs still require both OpenCode and `OPENCODE_BENCH_MODEL`.
- CI workflow now separates static checks, tests, examples, profile discovery, and harness dry-run into independent jobs with timeouts and a concurrency group.

### Repository readiness (2026-11-11)

- Expanded the README with installation references, configuration guidance, daily workflows, prompt patterns, cost optimization, FAQ, and a documentation index.
- Added light, dark, and mark logo variants under `assets/`.

- Updated all documentation with the public repository URL.
- Copied complete skill directories, including references, assets, and supporting scripts.
- Updated the installer to copy complete skill directories and back up existing skill trees.
- Added `working_directory` to benchmark tasks and made the harness execute tasks from the correct project directory.
- Added validation for benchmark task working directories and required task fields.
- Fixed the C# benchmark verification command to target the test project explicitly.
- Scoped `--clean` to the selected components and included `.ralph/hats`, while preserving `.ralph/agent` runtime state.
- Made `OPENCODE_BENCH_MODEL` required and passed it explicitly to `opencode run`, so both arms use the same model and avoid provider-default incompatibilities.
- Clarified completion promises for Ralph collections.
- Updated ast-grep version references to the verified 0.51.1 environment.

### Documentation comments (2026-11-11)

- Added AGENTS.md Section 2C and engineering rule 17: comments are documentation only.
- Standardized file headers for shell, Python, JSONC, YAML, agents, commands, and hats.
- Added function documentation blocks for shell functions and docstrings for Python functions.
- Added JSDoc for TypeScript exports and XML documentation for public C# types and members.
- Removed inline and field-level comments from configuration files; explanations live in `docs/`.
- Moved Ralph hat provenance and preset notes into a single standardized header block.

### Observability and release readiness (2026-11-11)

- Added `scripts/benchmarking/report_costs.py` to aggregate cost and token data from session artifacts.
- Added cost observability and MCP overhead documentation.
- Added the release checklist.
- Added an evidence-status table to the README and downgraded the hero claim to “production-oriented”.
- Adapted sourced commands to OpenCode subagent and question tools; all eight commands passed runtime smoke tests on the TypeScript fixture.
- Verified all ten skills through the OpenCode `skill` tool.

### Stabilization and validation (2026-11-11)

- Added `scripts/maintenance/run-ralph-isolated.sh` so Ralph runs in a separate clone and exports an unstaged patch.
- Added a macOS/Linux CI matrix for static validation, examples, OpenCode agent discovery, and harness dry-runs.
- Added the artifact compatibility matrix.
- Added the real-repository pilot index with pinned repositories and acceptance criteria.
- Extended command validation to require a valid target agent.

### Git safety (2026-11-11)

- Added AGENTS.md Section 2B: no automatic staging or commits by any agent, skill, command, hat, script, hook, orchestrator, or CI job.
- OpenCode permissions now deny `git add`, `git stage`, and `git commit` for agents.
- Every agent has an explicit local Git safety rule.
- Documented Ralph 2.10.1's landing auto-commit limitation and the separate-clone workaround.
- Removed the unimplemented `checkpoint_interval` key and documented the future default risk.
- Fixed the installer so `--dry-run` does not create backup directories.
- Ignored `.opencode-backup-*` directories in Git.
- Added validator enforcement that every agent resolves `git add`, `git stage`, and `git commit` to `deny` as the last matching rule.
- Extended deny patterns to `git -C`/`git -c` forms and to `git stash`, `git reset`, `git checkout`, and `git clean`.
- Updated Ralph examples to run only inside a separate disposable clone; worktrees are explicitly rejected.

### Author attribution (2026-11-11)

- Every skill now records `metadata.author`, `metadata.author_url`, and `metadata.author_email` when published.
- Every agent, command, and Ralph hat records `# author:`, `# author_url:`, and `# author_email:` in its provenance header.
- `docs/provenance/registry.yml` records the author for every artifact and source.
- The validator fails when author attribution is missing.
- No skill or agent is presented as original work; all are adapted from public repositories.

### Provenance remediation (2026-11-11)

- Added AGENTS.md Section 2A and engineering rule 15: no greenfield agents, skills, commands, hats, prompts, templates, examples, or benchmark tasks when a maintained upstream exists.
- Replaced all 12 locally authored agents with adapted agents from `VoltAgent/awesome-claude-code-subagents` and `wshobson/agents`.
- Replaced all 10 locally authored skills with skills from `obra/superpowers` and `wshobson/agents`.
- Replaced all 8 locally authored commands with commands from `wshobson/agents`.
- Replaced all 4 hat collections with Ralph's official `code-assist`, `review`, `research`, and `debug` presets, adding only per-hat OpenCode routing.
- Added `docs/provenance/registry.yml`, `docs/provenance/README.md`, and `THIRD_PARTY_NOTICES.md`.
- Added validator enforcement for provenance headers, skill metadata, and registry paths.
- Added `--clean` to the installer so removed artifacts do not linger in an existing installation.

### End-to-end verification (2026-11-11)

- OpenCode 2.2.7 loaded 19 agents in an isolated project (7 built-in + 12 custom).
- Serena 2.1.0 and CodeGraph 1.6.2 connected over MCP.
- TypeScript example: 7/7 tests pass.
- C# example: 4/4 tests pass.
- Ralph 2.10.1 completed the official `research` collection in 2 iterations with `RESEARCH_COMPLETE`.
- The official `code-assist` collection requires a larger iteration budget for multi-wave work; this is documented instead of hidden.

### Fixed during verification

- Ralph event syntax is XML (`<event topic="...">`), not `EVENT: ...`.
- Removed duplicate `default_publishes` from custom hats.
- Replaced `build.done` with `build.ready` to avoid Ralph's backpressure gate.
- Scoped `required_events` to the code-assist collection.
- Allowed transient temp directories so Ralph can pass large prompts.
- Coordinator may run shell commands for verification while remaining edit-denied.
- Replaced locally authored artifacts with pinned upstream versions (see Provenance remediation above).

### Known limitations

- OpenCode V2 does not run language servers; Serena replaces native LSP.
- No benchmark results are published; only methodology and harness.
- Ralph's OpenCode backend is plain text, so gates depend on exit codes.
