# Contributing

## Principles

1. Every recommendation must be reproducible with a command.
2. Label vendor claims as vendor claims.
3. Do not add a tool without documenting its token, runtime, license, and failure modes.
4. Do not commit credentials or machine-specific absolute paths.
5. Do not modify a user's existing OpenCode configuration automatically.

## Local checks

```bash
./scripts/validation/validate.sh
```

The validator checks JSON/JSONC/YAML syntax, required files, schema keys, and documentation links. The manual acceptance list is [docs/validation-checklist.md](docs/validation-checklist.md).

## Adding an agent

1. Create `agents/<role>/AGENT.md` with V2 frontmatter and instructions.
2. Add the installable copy path in the installer (the installer flattens to `.opencode/agents/<role>.md`).
3. Update `docs/agents/roles.md` and the delegation table.
4. Verify `opencode debug agents` lists it.

## Adding a skill

1. Create `skills/<name>/SKILL.md`.
2. Use a lowercase hyphenated name matching the directory.
3. Keep the description specific enough for the model to choose correctly.
4. Verify discovery with `opencode debug agents`; skills are listed by the native `skill` tool at runtime.

## Adding a Ralph hat

1. Add or extend a collection under `configs/ralph/hats/`.
2. Give each hat explicit `triggers`, `publishes`, and `instructions`.
3. Route to an OpenCode agent with `backend.args`.
4. Keep the number of hats small; do not duplicate responsibilities.

## Changing configuration

- Use only documented V2 fields. Validate against `https://opencode.ai/config.json`.
- Do not hardcode model identifiers. Use the routing overlay or environment variables.
- Run the validator before opening a pull request.

## Commit style

Conventional Commits: `docs:`, `feat:`, `fix:`, `chore:`, `ci:`.
