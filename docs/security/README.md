# Security

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** policy reviewed locally; no external audit

## Supported versions

| Component | Supported |
|---|---|
| This repository | `0.1.x` |
| OpenCode | `2.2.x` |
| Ralph Orchestrator | `2.10.x` |
| Python CLI | 3.11 or newer |

OpenCode V1 is not supported. See [compatibility policy](../compatibility/policy.md).

## Reporting a vulnerability

Use GitHub private vulnerability reporting on the repository:

<https://github.com/GabrielAlmeidaFlores/toolwright/security/advisories/new>

Do not open a public issue for a suspected vulnerability. Include reproduction steps, affected files, and impact. Do not include live credentials.

## Threat model

| Asset | Risk | Control |
|---|---|---|
| OpenCode configuration and agent prompts | A malicious prompt or instruction changes agent behaviour | Content is reviewed, sourced, and pinned; external text is treated as untrusted data |
| MCP servers | A server executes local commands with the user's privileges | Trust levels below; optional servers disabled by default |
| Installed profile | Overwriting a working configuration | Plan-by-default installer, backup before apply, lock file, rollback |
| Memory files | Secrets or stale guidance enter agent context | Credential scanner before write, TTL, reviewable Markdown |
| Pilot runner | Remote repository code executes during verification | Disposable clone, pinned commit, isolated workspace, no Ralph |
| Git history | Automation writes commits the human did not review | Git write commands denied; no auto-stage or auto-commit |

This is **not** a sandbox. OpenCode permissions and this repository's deny rules are defense-in-depth; they do not contain a determined local process.

## MCP trust levels

| Level | Meaning | Default |
|---|---|---|
| `reviewed` | Source and command reviewed; enabled in the profile | Serena, CodeGraph |
| `local` | Runs a binary the user installed and trusts | Allowed when explicitly enabled |
| `untrusted` | Downloads or executes remote code, or has unclear provenance | Disabled |

Rules:

- Do not enable an MCP server you have not reviewed.
- Prefer a pinned binary or package over `npx -y` for long-lived use.
- Treat tool descriptions and tool output as untrusted input.
- A server that needs credentials should read them from the environment, never from a committed file.

## Prompt injection

External documentation, issues, web pages, and repository content are data. Agents must not treat embedded instructions as authorization to run commands, read secrets, change permissions, or install software.

## Secrets

- `.env` and machine-local files are gitignored.
- `toolwright memory add` rejects text that matches common credential patterns.
- Reports and artifacts must not include credentials.
- Rotate immediately if a secret is committed, even after removal from the working tree.

## Dependencies and licenses

The repository is MIT. Third-party artifacts keep their licenses; see `THIRD_PARTY_NOTICES.md` and `docs/provenance/registry.yml`.

## Scope

In scope: this repository's scripts, CLI, configuration, agent and skill content, catalog, memory, and pilot runner.

Out of scope: the security of third-party agents, MCP servers, model providers, and OpenCode itself. Report those upstream.

## References

- [Support](https://github.com/GabrielAlmeidaFlores/toolwright/blob/main/SUPPORT.md)
- [Release process](../release/README.md)
- [Validation checklist](../validation-checklist.md)
