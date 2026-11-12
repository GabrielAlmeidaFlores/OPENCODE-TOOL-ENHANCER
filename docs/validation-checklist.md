# Validation Checklist

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally

Run the automated checks first:

```bash
make ci
```

`make ci` runs the validator and the unit and integration suites. Run the individual
targets during development:

```bash
make validate   # validator only
make test       # unit and integration tests
make lint       # shell syntax and ShellCheck
```

Then complete the manual checks for your environment.

## Repository

- [ ] `./scripts/validation/validate.sh` prints `OK`.
- [ ] `python3 -m unittest discover -s tests -t .` passes.
- [ ] `VERSION` contains a semantic version.
- [ ] JSON/JSONC files parse and contain `$schema`.
- [ ] Ralph YAML files parse.
- [ ] All 12 agent files exist with valid `mode`.
- [ ] All 10 skills exist with a matching `name` and provenance metadata.
- [ ] Every agent, command, and hat has a provenance header.
- [ ] `docs/provenance/registry.yml` points only to existing local paths.
- [ ] Every `docs/` page outside `decisions/` has status, last-verified, and evidence fields.
- [ ] Comments follow AGENTS.md Section 2C across `scripts/`, `packages/`, `skills/`, and `tests/`: file headers and contract docstrings only, with block-form Python docstrings when present, JSDoc for TypeScript, and XML documentation for C#.
- [ ] No inline comments or commented-out code in scripts, configs, or examples.
- [ ] Relative documentation links resolve.
- [ ] External links use maintained sources (run `--links` when useful).

## CLI

- [ ] `python3 -m pip wheel ./packages/ote_cli --no-deps` builds a wheel.
- [ ] `ote --version` matches `VERSION`.
- [ ] `ote doctor --json` exits 0 with no failures.
- [ ] `ote install --dry-run` lists files and writes nothing.
- [ ] `ote install --apply` writes a lock and state, and a second apply reports `already up to date`.
- [ ] `ote update --check` exits 0 on a clean target and 1 after a managed file is modified.
- [ ] `ote uninstall` without `--yes` refuses; with `--apply --yes` removes only unmodified managed files.
- [ ] `ote rollback` lists backups without changing files.

## Stats, evals, and pilots

- [ ] `ote stats` renders Markdown, JSON, and CSV from result artifacts.
- [ ] Baseline and optimized runs produce a comparison row.
- [ ] `ote stats --budget` exits 1 when recorded cost exceeds the ceiling.
- [ ] `ote eval` passes with no model call.
- [ ] `ote pilot list` shows the three selected repositories.
- [ ] `ote pilot run hono --dry-run` prints the planned commands and writes nothing.
- [ ] A real pilot records verification, cost, tokens, and tool errors under `artifacts/`.

## Memory and specs

- [ ] `ote memory add` writes one entry and updates `catalog.md`.
- [ ] `ote memory search` finds title, body, source, and type.
- [ ] A credential-shaped string is rejected.
- [ ] Expired entries are excluded from the preamble and removed by `prune --apply --yes`.
- [ ] `ote memory preamble` stays within the configured budget.
- [ ] `ote spec new` creates four artifacts.
- [ ] `ote spec plan` fails until every criterion has a task.
- [ ] `ote spec verify` fails until every criterion has evidence.
- [ ] `user/` memory is gitignored; `project/` and `shared/` are tracked.

## Verification and governance

- [ ] `ote verify --only validate` exits 0.
- [ ] `ote verify --only lint` exits 0.
- [ ] `ote verify --json` reports a summary and failure classes.
- [ ] A failing check exits 1 and a missing check name exits 2.
- [ ] `ote govern contracts` reports zero failures.
- [ ] `ote govern gate --risk high` lists verify, review, and security.
- [ ] `ote govern check --record` blocks a record over budget.
- [ ] `.ote/cache/` is gitignored.

## Profiles and catalog

- [ ] `ote profile verify` exits 0 for every manifest.
- [ ] `ote profile use minimal --target /tmp/check --dry-run` lists files and writes nothing.
- [ ] `ote catalog verify` reports zero failures.
- [ ] `ote catalog verify --check-drift` matches `docs/provenance/registry.yml`.
- [ ] `python3 scripts/catalog/build_catalog.py --check` exits 0.
- [ ] `ote compat --json` returns the V1/V2 matrix.
- [ ] Adding a provenance entry and regenerating changes both catalog files together.

## OpenCode

- [ ] `opencode --version` is `2.2.x`.
- [ ] `.opencode/opencode.jsonc` is in place.
- [ ] `opencode debug agents` lists `coordinator` and eleven subagents.
- [ ] `opencode debug agents` shows `coordinator` as `primary`.
- [ ] Read-only agents deny `edit`.
- [ ] Every subagent denies `subagent` (no recursion).
- [ ] `opencode mcp list` shows Serena and CodeGraph connected, or they are disabled.
- [ ] A denied action (for example `sudo`) is actually blocked.
- [ ] `git add`, `git stage`, `git commit`, and the `git -C`/`git -c`/stash/reset/checkout/clean variants resolve to `deny` at the end of every agent permission list (agent rules override global rules).
- [ ] No workflow stages or commits automatically.
- [ ] Ralph examples run only in a separate disposable clone, not a linked worktree.

## Tooling

- [ ] `rg --version` works.
- [ ] `ast-grep --version` works.
- [ ] `serena --version` works and `serena start-mcp-server --help` runs.
- [ ] `codegraph --version` works and `codegraph init` created `.codegraph/`.
- [ ] Startup time is acceptable on a representative project.

## Ralph

- [ ] `ralph --version` reports `2.10.x`.
- [ ] `ralph preflight -c .ralph/ralph.yml --format human` passes or warnings are understood.
- [ ] A dry run shows `opencode run --agent <role>`.
- [ ] The `research` workflow reaches `RESEARCH_COMPLETE` on a small question.
- [ ] `code-assist` runs with a sufficient iteration budget for multi-wave work.
- [ ] `scripts/maintenance/run-ralph-isolated.sh --dry-run` prints the isolated plan.
- [ ] A deliberately failing test blocks completion.
- [ ] `.ralph/agent/scratchpad.md` contains the iteration state.

## Examples

- [ ] `examples/typescript`: `npm install && npm test` passes.
- [ ] `examples/csharp`: `dotnet test Example.Tests/Example.Tests.csproj` passes.
- [ ] The multi-agent example documents the expected event flow.

## Runtime smoke

- [ ] All eight commands respond on the TypeScript fixture.
- [ ] All ten skills load through the `skill` tool.
- [ ] `python3 scripts/benchmarking/report_costs.py` runs without error.
- [ ] MCP overhead evidence is current.

## Task board and plugin

- [ ] `ote task add` creates a task and regenerates `BOARD.md`.
- [ ] The WIP limit blocks a third in-progress task with the default configuration.
- [ ] Moving to `done` requires `--approved`.
- [ ] A worktree is created only on request and is gitignored.
- [ ] Removing a worktree requires `--remove --yes`.
- [ ] `node --check configs/opencode/plugins/ote-memory.js` passes.
- [ ] The plugin is absent from the minimal and standard profiles.
- [ ] The plugin does nothing without `.ote/memory/plugin.enabled`.

## Docs site and release

- [ ] `mkdocs build --strict` passes.
- [ ] `python3 scripts/release/check_version.py` passes.
- [ ] `python3 scripts/maintenance/check_upstream_drift.py --offline` lists every source.
- [ ] `SECURITY.md`, `SUPPORT.md`, `ROADMAP.md`, and `CODE_OF_CONDUCT.md` exist.
- [ ] The release and upstream-drift workflows parse as valid YAML.

## Documentation

- [ ] Every command in the quick start was executed.
- [ ] No V1-only command is presented as current.
- [ ] Vendor claims are labelled as vendor claims.
- [ ] No benchmark result is published without correctness data.
