# Security Policy

## Supported versions

- This repository: `0.1.x`
- OpenCode: `2.2.x`
- Ralph Orchestrator: `2.10.x`
- Python: 3.11 or newer

OpenCode V1 is unsupported. See `docs/compatibility/policy.md`.

## Reporting

Use GitHub private vulnerability reporting:

<https://github.com/GabrielAlmeidaFlores/toolwright/security/advisories/new>

Do not open a public issue for a suspected vulnerability. Include affected files, reproduction steps, and impact. Never include live credentials.

## Scope

In scope: this repository's CLI, scripts, configuration, agent and skill content, catalog, memory store, and pilot runner.

Out of scope: OpenCode itself, model providers, and third-party MCP servers. Report those upstream.

## Baseline controls

- No automatic staging or commits.
- Installer plans by default; apply requires an explicit flag and writes a backup.
- Git write commands are denied for agents and validated.
- Memory writes reject common credential patterns.
- Optional MCP servers are disabled by default.
- Pilots run in disposable clones.

Full threat model and MCP trust levels: `docs/security/README.md`.
