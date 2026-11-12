# Roadmap

Status reflects the repository, not intentions.

| Phase | Scope | Status |
|---|---|---|
| 0 | Baseline, version, docs status, decisions | Complete |
| 1 | Green CI, offline test suite, harness fix | Complete |
| 2 | `ote` CLI, lock file, install lifecycle | Complete |
| 3 | Profiles, verified catalog, compatibility matrix | Complete |
| 4 | Verification engine, governance, risk gates | Complete |
| 5 | Markdown memory, spec workflow | Complete |
| 6 | Stats, deterministic evals, pilot runner | Complete |
| 7 | Docs site, security/support/roadmap, release automation, drift checks | Complete |
| 8 | Optional Markdown task board and OpenCode plugin | Planned |

## Next after Phase 7

- Execute the full five-task pilots and publish results with correctness, cost, and rework. The Hono runner smoke is complete and is not a pilot result.
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
