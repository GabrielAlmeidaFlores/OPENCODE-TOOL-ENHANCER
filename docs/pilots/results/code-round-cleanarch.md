# CleanArchitecture Code-Change Pilot

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** build and unit tests passed; no SQL Server functional run

Five code-change tasks on `ardalis/CleanArchitecture` at `302e8ac4d6`. Each ran in a disposable clone with a locally installed .NET 11 preview SDK and the `backend-developer` agent.

## Environment adaptation

The repository pins .NET SDK `11.0.100`; only .NET 10 was installed. A local .NET 11 RC SDK was installed under `/tmp/dotnet11`, and the clone's `global.json` was updated in the disposable setup step. Unit-test execution required `DOTNET_ROLL_FORWARD_TO_PRERELEASE=1`.

## Results

| Task | Change | Verification | Cost | Tokens in/out |
|---|---|---|---|---|
| Bug | Fix bracketed `sp_rename` names in `UseDbGeneratedIds` Up/Down | Infrastructure build | $0.008579 | 19,458 / 3,611 |
| Feature | Expose `ContributorStatus` in list/get/update responses | Solution build + 14 unit tests | $0.000000 (free) | 67,729 / 8,019 |
| Refactor | Extract contributor route templates | Solution build + 14 unit tests | $0.018247 | 78,622 / 4,799 |
| Security | Move `UseHttpsRedirection` before `UseFastEndpoints` | Solution build + 14 unit tests | $0.006886 | 18,335 / 2,300 |
| Performance | Validate pagination page/perPage bounds | Solution build + 14 unit tests | $0.031444 | 48,503 / 11,225 |

All five published runs had `opencode_exit = 0` and `verification_exit = 0`.

## Rework

- The feature task first ended on an unavailable Web Search request after tests passed; it was rerun without Web Search.
- A test-host runtime mismatch required enabling prerelease roll-forward.

## Limitations

- Unit tests only; SQL Server Testcontainers/functional tests were not executed.
- The .NET 11 preview SDK and `global.json` patch are pilot-environment adaptations, not upstream-compatible changes.
- Diffs were not independently reviewed.
- No change was proposed upstream or committed to the project checkout.

## References

- `docs/pilots/results/round-1.md`
- `docs/pilots/results/cleanarch/`
