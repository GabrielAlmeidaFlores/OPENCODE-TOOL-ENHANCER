# Support

## Before asking

1. Read `docs/troubleshooting/README.md` and `docs/troubleshooting/ci.md`.
2. Run `toolwright doctor` and include its output.
3. Run `make ci` or `make validate` and include the failing check.
4. Check `docs/RELEASE_CHECKLIST.md` and `docs/validation-checklist.md`.

## Where to ask

| Topic | Channel |
|---|---|
| Bug in this repository | GitHub issue with reproduction steps |
| Security vulnerability | Private advisory, see `SECURITY.md` |
| OpenCode behaviour | <https://github.com/anomalyco/opencode/issues> |
| Ralph Orchestrator | <https://github.com/mikeyobrien/ralph-orchestrator/issues> |
| Serena | <https://github.com/oraios/serena/issues> |
| CodeGraph | <https://github.com/colbymchenry/codegraph/issues> |

## What to include

- Commit or version (`git rev-parse HEAD`, `toolwright --version`, `opencode --version`)
- Operating system and shell
- Exact command and full error output
- Which profile was installed
- Whether the issue reproduces in a clean temporary target

## Scope

This is a community project without a response-time guarantee. Support covers the artifacts in this repository. Third-party tools are supported by their maintainers.
