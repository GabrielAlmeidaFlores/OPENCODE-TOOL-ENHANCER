# Validation Checklist

Run the automated checks first:

```bash
./scripts/validation/validate.sh
```

Then complete the manual checks for your environment.

## Repository

- [ ] `./scripts/validation/validate.sh` prints `OK`.
- [ ] JSON/JSONC files parse and contain `$schema`.
- [ ] Ralph YAML files parse.
- [ ] All 12 agent files exist with valid `mode`.
- [ ] All 10 skills exist with a matching `name` and provenance metadata.
- [ ] Every agent, command, and hat has a provenance header.
- [ ] `docs/provenance/registry.yml` points only to existing local paths.
- [ ] Comments follow AGENTS.md Section 2C: file headers and function documentation only.
- [ ] No inline comments or commented-out code in scripts, configs, or examples.
- [ ] Relative documentation links resolve.
- [ ] External links use maintained sources (run `--links` when useful).

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
- [ ] A deliberately failing test blocks completion.
- [ ] `.ralph/agent/scratchpad.md` contains the iteration state.

## Examples

- [ ] `examples/typescript`: `npm install && npm test` passes.
- [ ] `examples/csharp`: `dotnet test Example.Tests/Example.Tests.csproj` passes.
- [ ] The multi-agent example documents the expected event flow.

## Documentation

- [ ] Every command in the quick start was executed.
- [ ] No V1-only command is presented as current.
- [ ] Vendor claims are labelled as vendor claims.
- [ ] No benchmark result is published without correctness data.
