# Contributing

## Principles

1. **Source before writing.** No agent, skill, command, hat, prompt, template, example, or benchmark task may be authored from scratch when a maintained upstream exists. See `AGENTS.md` Section 2A and `docs/provenance/registry.yml`.
2. Every recommendation must be reproducible with a command.
2. Label vendor claims as vendor claims.
3. Do not add a tool without documenting its token, runtime, license, and failure modes.
4. Do not commit credentials or machine-specific absolute paths.
5. Do not modify a user's existing OpenCode configuration automatically.
6. Record provenance before opening a pull request.

## Repository

https://github.com/GabrielAlmeidaFlores/toolwright

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

1. Start from an official Ralph preset under `presets/`.
2. Extract only the `event_loop` and `hats` sections.
3. Add per-hat `backend.args` for OpenCode agent routing.
4. Keep the upstream instructions unchanged; record the diff in the file header and registry.
5. Validate with `ralph preflight` and `ralph run --dry-run`.

## Changing configuration

- Use only documented V2 fields. Validate against `https://opencode.ai/config.json`.
- Do not hardcode model identifiers. Use the routing overlay or environment variables.
- Run the validator before opening a pull request.

## Comment style

Follow `AGENTS.md` Section 2C.

- Use one file header block with purpose, usage, validation, and references.
- Document every function with the native format: Python docstring, shell function block, JSDoc, or XML documentation.
- Do not use inline comments, commented-out code, decorative separators, or field-level comments in configuration.
- Move decision explanations to `docs/` instead of leaving them beside code.

## Commit style

Conventional Commits: `docs:`, `feat:`, `fix:`, `chore:`, `ci:`.
