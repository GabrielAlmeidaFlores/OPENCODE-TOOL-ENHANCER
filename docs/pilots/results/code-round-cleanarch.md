# CleanArchitecture Code-Change Pilot

> **Status:** Experimental · **Last verified:** 2026-11-13 · **Evidence:** build, unit tests, and 10–17 functional tests passed per task on .NET 11 with a documented reference workaround; all five changes are production-ready after review

Five code-change tasks on `ardalis/CleanArchitecture` at `302e8ac4d6`. Each ran in a disposable clone with a locally installed .NET 11 SDK and the `backend-developer` agent.

## Environment adaptation

The repository pins .NET SDK `11.0.100`; only .NET 10 was installed. .NET 11 RC3 was installed under `/tmp/dotnet11` for the pilot runs and .NET 11 GA (`11.0.100`) under `/tmp/dotnet11ga` for the functional-test runs. The disposable clone's `global.json` was updated to the installed SDK, and unit-test execution required `DOTNET_ROLL_FORWARD_TO_PRERELEASE=1`.

The functional-test project did not compile under the .NET 11 SDK: transitive project and package references were absent from `project.assets.json` (`Microsoft.EntityFrameworkCore` and then `Clean.Architecture.Core` could not be resolved). A minimal reproduction with three plain projects showed .NET 10 flowing the same references but .NET 11 not flowing them. For the pilot, the disposable functional-test project received explicit references to the packages and `Clean.Architecture.Core` it already used transitively. This is a test-environment workaround; it does not change product code or behavior.

## Results

| Task | Change | Verification | Cost | Tokens in/out |
|---|---|---|---|---|
| Bug | Fix bracketed `sp_rename` names in `UseDbGeneratedIds` Up/Down | Infrastructure build | $0.008579 | 19,458 / 3,611 |
| Feature | Expose `ContributorStatus` in list/get/update responses | Solution build + 14 unit tests | $0.000000 (free) | 67,729 / 8,019 |
| Refactor | Extract contributor route templates | Solution build + 14 unit tests | $0.018247 | 78,622 / 4,799 |
| Security | Move `UseHttpsRedirection` before `UseFastEndpoints` | Solution build + 14 unit tests | $0.006886 | 18,335 / 2,300 |
| Performance | Validate pagination page/perPage bounds | Solution build + 14 unit tests | $0.031444 | 48,503 / 11,225 |

All five published runs had `opencode_exit = 0` and `verification_exit = 0`.

## Functional tests

The SQL Server and SQLite functional suite was executed separately on each task clone with the .NET 11 GA SDK and a running Docker daemon:

| Task | Functional tests | Result |
|---|---|---|
| Bug | 12 | Passed |
| Feature | 10 | Passed |
| Refactor | 10 | Passed |
| Security | 15 | Passed |
| Performance | 17 | Passed |

The suite includes `Testcontainers.MsSql` SQL Server tests, SQLite fallback tests, and endpoint tests. The untouched base clone passes the same 10-test baseline with the reference workaround, so the task results are not caused by the workaround. The security task added five HTTPS-redirection tests.

## Independent review

A separate reviewer agent read each diff and built the solution. Verdicts:

| Task | Verdict | Main finding |
|---|---|---|
| Bug (`sp_rename`) | Production-ready | Root cause fixed in `Up` and `Down`; the added regression test is textual and is not part of the unit-test gate |
| Feature (`ContributorStatus`) | Production-ready | Mapping is consistent; a legacy status value outside 1–3 would now fail the list endpoint instead of being ignored |
| Refactor (`ContributorRoutes`) | Production-ready | Behavior-preserving; the doc comment overstates centralization because list/create still hard-code the route |
| Security (HTTPS redirect order) | Production-ready after rerun | First version activated the redirect without forwarded-header handling; the rerun adds forwarded headers, secure loopback-only defaults, an explicit HTTPS port, and spoofing/redirect tests |
| Performance (pagination) | Production-ready | Overflow guard is correct; `per_page` above the maximum now clamps to 200 instead of returning 400, a deliberate contract change that needs approval |

The sub-agent could not complete every unit-test run because of a test-host hang, so the build and static review carried more weight for tasks 3–5. The functional suite above was executed separately and passed.

## Rework

- The feature task first ended on an unavailable Web Search request after tests passed; it was rerun without Web Search.
- A test-host runtime mismatch required enabling prerelease roll-forward.
- The security task was rerun twice: the first version trusted forwarded headers from every source, and the second added the tests needed to prove the secure default.

## Limitations

- The .NET 11 SDK and `global.json` patch are pilot-environment adaptations. The functional-test project also required explicit references that upstream does not declare; without them the baseline project does not compile under .NET 11.
- The functional suite counts differ because task 1 added a migration test and task 5 added pagination cases.
- Task 4 is production-ready with `ForwardedHeaders:Enabled=false` by default; operators behind a proxy must enable it and configure trusted proxies or networks. The test-host hang prevented a final clean unit-test run, but 12/12 unit tests passed during the pilot run and the product code did not change afterward.
- Task 5's clamp contract change needs product approval.
- No change was proposed upstream or committed to the project checkout.

## References

- `docs/pilots/results/round-1.md`
- `docs/pilots/results/cleanarch/`
