# Real-Repository Pilots

The pilots validate the profile on real codebases instead of only the bundled fixtures. They are separate from the deferred benchmark program and do not claim statistical cost results.

## Selected repositories

| Repository | Stack | Pinned commit | License | Pilot focus |
| --- | --- | --- | --- | --- |
| [honojs/hono](https://github.com/honojs/hono) | TypeScript | `f6fbaf0299c48eea9e656e03e2ffe7ac755e8823` | MIT | Routing, middleware, tests |
| [ardalis/CleanArchitecture](https://github.com/ardalis/CleanArchitecture) | C# | `302e8ac4d631f45f015413950dcb97d0d146169b` | MIT | Validation, endpoints, tests |
| [vercel/turborepo](https://github.com/vercel/turborepo) | Multi-language monorepo | `4e3bdf1eff825764acff269b8e71760e5e5c9300` | MIT | Package boundaries, dependency graph |

## Procedure

1. Clone the pinned commit into a disposable directory.
2. Install the project dependencies.
3. Install this profile into the clone with the installer.
4. Run five representative tasks:
   - one bug fix with a regression test
   - one small feature with tests
   - one refactor without behavior change
   - one security or input-validation fix
   - one performance or dependency investigation
5. Record:
   - task prompt and acceptance criteria
   - exact verification command and result
   - agent used
   - model and variant
   - input and output tokens
   - cost
   - wall time
   - rework and human interventions
   - files changed
6. Store the report under `docs/pilots/<repository>/`.
7. Promote configuration or agent fixes discovered during the pilot.

## Acceptance criteria

- Five tasks per repository.
- Every task has a rerunnable verification command.
- Correctness is reviewed independently from the implementing agent.
- At least one real defect or friction point is documented per repository.
- No critical blocker remains before the pilot is marked complete.

## Current status

| Pilot | Status |
| --- | --- |
| `honojs/hono` | Selected; execution pending |
| `ardalis/CleanArchitecture` | Selected; execution pending |
| `vercel/turborepo` | Selected; execution pending |

## Constraints

- Do not run Ralph in the pilot checkout without `scripts/maintenance/run-ralph-isolated.sh`.
- Do not run benchmarks that modify the repository without a disposable copy.
- Do not publish cost claims from a single run.
- Keep model identifiers in environment variables, not in committed configuration.
