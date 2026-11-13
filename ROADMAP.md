# Roadmap

Status reflects the repository, not intentions. All planned phases are complete.

| Phase | Scope | Status |
|---|---|---|
| 0 | Baseline, version, docs status, decisions | Complete |
| 1 | Green CI, offline test suite, harness fix | Complete |
| 2 | `toolwright` CLI, lock file, install lifecycle | Complete |
| 3 | Profiles, verified catalog, compatibility matrix | Complete |
| 4 | Verification engine, governance, risk gates | Complete |
| 5 | Markdown memory, spec workflow | Complete |
| 6 | Stats, deterministic evals, pilot runner | Complete |
| 7 | Docs site, security/support/roadmap, release automation, drift checks | Complete |
| 8 | Optional Markdown task board and OpenCode plugin | Complete |

## Next after Phase 7

- Discovery round 1 is complete: 15/15. Code-change rounds: Hono 5/5 independently reviewed; CleanArchitecture 5/5 independently reviewed with build, unit, and SQL Server functional tests; turborepo 4/5 verified with one task rejected in review.
- Evaluate optional task board and memory-injection plugin only after the CLI, memory, and observability are stable.
- Keep benchmarks deferred until correctness and rework measurement is reproducible.

## Explicit non-goals

- A large agent catalog; the project keeps twelve focused roles.
- A vector database, daemon, A2A hub, or web UI.
- A second orchestrator beside Ralph.
- Automatic commits, staging, or merges.
- Self-modifying or self-learning loops without evaluation.

## Evidence

Each phase is complete only when its acceptance criteria and CI checks pass. See `docs/RELEASE_CHECKLIST.md`, `docs/validation-checklist.md`, and the CI runs linked from the README.
