# GitHub Copilot

> **Status:** Experimental · **Last verified:** 2026-11-13 · **Evidence:** Copilot CLI 1.0.105 discovered the generated repository instruction, 12 path instructions, and 10 project skills; prompt files and runtime behavior not inspected

GitHub Copilot reads repository instructions from `.github/copilot-instructions.md`, path-specific files under `.github/instructions/`, and the nearest `AGENTS.md`. ToolWright generates all three, plus skills and prompt files. Copilot does not use OpenCode agents or permissions, so the generated files carry guidance rather than an orchestration runtime.

## Install with ToolWright

```bash
toolwright install --platform copilot --profile minimal --target /path/to/project --apply
```

Update with the same command and remove with:

```bash
toolwright uninstall --target /path/to/project --apply --yes
```

The lock records each generated path, its generator, and its digest. Existing destination files are backed up before the adapter overwrites them.

## Generated files

| Path | Source |
|---|---|
| `.github/copilot-instructions.md` | `AGENTS.md` |
| `AGENTS.md` | `AGENTS.md` |
| `.github/instructions/<role>.instructions.md` | `agents/<role>/AGENT.md` |
| `.github/prompts/<name>.prompt.md` | `commands/<name>.md` |
| `.github/skills/<name>/` | `skills/<name>/` |

## Files

| File | Scope |
|---|---|
| `.github/copilot-instructions.md` | Repository-wide rules |
| `.github/instructions/<name>.instructions.md` | Rules for matching paths; requires `applyTo` frontmatter |
| `AGENTS.md` | Agent instructions; the nearest file wins |
| `.github/prompts/<name>.prompt.md` | Reusable prompt files in supported IDE clients |

## Role mapping

The adapter writes one `.github/instructions/<role>.instructions.md` file per agent.

| ToolWright role | Copilot representation |
|---|---|
| `coordinator` | Repository instructions: plan, delegate, verify |
| `planner` | Prompt file or path instruction for planning |
| `code-reviewer` | Path instruction for changed source files |
| `security-reviewer` | Path instruction for security-sensitive paths |
| `test-engineer` | Path instruction for test files and verification commands |
| `documentation-engineer` | Path instruction for `docs/**` |

## Repository-wide example

```markdown
# .github/copilot-instructions.md

- Run `make validate`, `make test`, and `make lint` before proposing a change.
- Never stage or commit automatically. Leave changes unstaged.
- Prefer the existing agent, command, and skill contracts over new abstractions.
- Do not claim runtime behavior that was not executed.
```

## Path-specific example

```markdown
---
applyTo: "**/*.ts,**/*.tsx,**/*.cs"
---
Review for correctness, behavior changes, missing tests, and security issues.
Return findings in severity order with file and line references. Do not edit files.
```

## Customize the mapping

The adapter generates the files. Edit installed files only when you need repository-specific guidance:

1. Keep project-wide rules in `.github/copilot-instructions.md` or `AGENTS.md`.
2. Add path filters to `.github/instructions/*.instructions.md` when a role should apply only to matching files.
3. Keep verification commands identical to the repository's `Makefile` or CI.

## Limits

- Copilot does not enforce OpenCode's per-agent edit/shell permissions.
- Copilot does not provide Ralph orchestration or ToolWright's subagent tree.
- Runtime availability of prompt files and path instructions varies by Copilot client and plan.
- The Copilot CLI listed `.github/copilot-instructions.md` and every `.github/instructions/*.instructions.md` file. It did not list `AGENTS.md` while the repository instruction file was present, even though the adapter writes both.
- The CLI has no inspection command for `.github/prompts/`; prompt-file discovery remains unverified.

## Verify

Run these commands inside the generated target:

```bash
copilot instruction list
copilot skill list
```

Expected on Copilot CLI `1.0.105`:

- `instruction list` reports `.github/copilot-instructions.md` and 12 role instruction files.
- `skill list` reports the 10 installed project skills.

For a runtime check, open the repository in a supported client and ask Copilot to summarize the repository instructions.

## References

- [GitHub Docs: repository custom instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- [AGENTS.md](https://agents.md)
- `../installation/adapter-validation.md`
