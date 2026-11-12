# Pilot Feature: Expose Contributor Status in Contributor Responses

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** pilot output, structurally verified, not independently reviewed

| | |
|---|---|
| **Status** | Proposed |
| **Area** | Contributors read model (list, get-by-id, update response) |
| **Size** | Small — additive response change, no schema change, no migration |
| **Risk** | Low — existing fields and request payloads are unchanged |

## Summary

The `Contributor` aggregate stores a status (`CoreTeam`, `Community`, or `NotSet`), and that status is persisted and seeded, but it is never returned by the HTTP API. Add a `status` field to the contributor representation used by `GET /Contributors`, `GET /Contributors/{id}`, and the `contributor` object in the `PUT /Contributors/{id}` response.

The value is serialized as the smart-enum **name** (for example, `"CoreTeam"`), not its numeric value, so the payload is readable and stable.

## Motivation

- The domain already owns the value: `Contributor.Status` is part of the aggregate at `src/Clean.Architecture.Core/ContributorAggregate/Contributor.cs:8`.
- Persistence is already configured with a value converter at `src/Clean.Architecture.Infrastructure/Data/Config/ContributorConfiguration.cs:21-24`, and the `Status` column already exists in the schema (for example `src/Clean.Architecture.Infrastructure/Data/Migrations/20231218143922_PhoneNumber.cs:20`).
- Seed data already writes status values at `src/Clean.Architecture.Infrastructure/Data/SeedData.cs:21-27`.
- Despite this, the read contracts drop the value: `ContributorDto` has no status (`src/Clean.Architecture.UseCases/Contributors/ContributorDTO.cs:4`), `ContributorRecord` has no status (`src/Clean.Architecture.Web/Contributors/ContributorRecord.cs:3`), and the handlers/mappers build those objects without it (`src/Clean.Architecture.UseCases/Contributors/Get/GetContributorHandler.cs:18`, `src/Clean.Architecture.Web/Contributors/List.cs:127`).
- Result: API consumers cannot distinguish a core-team contributor from a community contributor or an unclassified one, even though the database can.

## Proposed Behavior

1. `GET /Contributors` items gain a `status` string field. Pagination metadata is unchanged.
2. `GET /Contributors/{id}` gains the same `status` field.
3. `PUT /Contributors/{id}` gains `status` inside the nested `contributor` object, reflecting the persisted status.
4. The wire values are exactly `"CoreTeam"`, `"Community"`, or `"NotSet"` (the `SmartEnum.Name` values defined at `src/Clean.Architecture.Core/ContributorAggregate/ContributorStatus.cs:5-7`).
5. The feature is read-only: create/update request bodies do not accept status, and no new endpoint or query parameter is introduced.

Example list response (illustrative):

```json
{
  "items": [
    { "id": 1, "name": "Ardalis", "phoneNumber": "+1 555-555-5555", "status": "CoreTeam" },
    { "id": 2, "name": "Ilyana", "phoneNumber": "Unknown", "status": "NotSet" }
  ],
  "page": 1,
  "perPage": 10,
  "totalCount": 27,
  "totalPages": 3
}
```

## Acceptance Criteria

1. **List exposes status.** Every item returned by `GET /Contributors` contains a non-null `status` whose value is one of `CoreTeam`, `Community`, or `NotSet` and matches the seeded/row value. Existing fields (`id`, `name`, `phoneNumber`) and pagination fields (`page`, `perPage`, `totalCount`, `totalPages`) keep their current names, types, and values.
2. **Get-by-id exposes status.** `GET /Contributors/{id}` returns `status` for an existing contributor and still returns 404 for an unknown id.
3. **Update response stays consistent.** `PUT /Contributors/{id}` returns the nested `contributor` object with the same `status` the row had before the update (the update must not reset status).
4. **Name, not number.** Responses serialize the smart-enum name (for example `"CoreTeam"`), never the numeric value `1/2/3`, and never a .NET type name.
5. **Works on both providers.** The list query works on SQL Server and SQLite; adding status must not produce `Invalid column name 'Status'` when EF composes over the `FromSqlRaw` projection.
6. **No database migration.** No new migration file is required because the `Status` column already exists; `dotnet ef migrations` is not part of this change.
7. **Non-default status is observable in tests.** Seed at least one contributor with `ContributorStatus.CoreTeam` (for example contributor 1) so functional tests can assert a value other than `NotSet`, without changing `SeedData.NUMBER_OF_CONTRIBUTORS`.
8. **Tests pass.** Existing unit/integration/functional tests continue to pass, and new assertions cover list, get-by-id, and update responses.
9. **API documentation matches.** Swagger response examples for list, get-by-id, and update include `status`.
10. **Additive contract only.** No existing JSON property is renamed, removed, or retyped, and no request contract changes.

## Implementation Notes (file:line references)

- **Domain value and display name** — use `ContributorStatus.Name`; the allowed values are defined at `src/Clean.Architecture.Core/ContributorAggregate/ContributorStatus.cs:5-7`, and the aggregate property is at `src/Clean.Architecture.Core/ContributorAggregate/Contributor.cs:8`.
- **Use-case read model** — extend `ContributorDto` with a `ContributorStatus Status` component at `src/Clean.Architecture.UseCases/Contributors/ContributorDTO.cs:4`, following the existing pattern of carrying domain value objects in the DTO.
- **Get handler** — pass `entity.Status` when constructing the DTO at `src/Clean.Architecture.UseCases/Contributors/Get/GetContributorHandler.cs:18`.
- **Update handler** — pass `existingContributor.Status` when constructing the DTO at `src/Clean.Architecture.UseCases/Contributors/Update/UpdateContributorHandler.cs:21-22`.
- **List query (primary risk)** — the raw SQL projection at `src/Clean.Architecture.Infrastructure/Data/Queries/ListContributorsQueryService.cs:19` currently selects only `Id`, `Name`, and phone columns. Add `Status` to that `SELECT` list, then project `c.Status` into the DTO at `src/Clean.Architecture.Infrastructure/Data/Queries/ListContributorsQueryService.cs:23`. EF composes `ORDER BY`/`SKIP`/`TAKE` over this raw SQL, so the column must be present in the subquery.
- **Fake list service** — update the in-memory DTO construction at `src/Clean.Architecture.Infrastructure/Data/Queries/FakeListContributorsQueryService.cs:15` so test/dev implementations stay compile-compatible.
- **HTTP response record** — add a `string Status` component to `ContributorRecord` at `src/Clean.Architecture.Web/Contributors/ContributorRecord.cs:3`. This is a positional record, so every construction site must be updated.
- **Web mappers and examples** — update the list mapper and example at `src/Clean.Architecture.Web/Contributors/List.cs:127` and `src/Clean.Architecture.Web/Contributors/List.cs:25-26`; the get mapper and example at `src/Clean.Architecture.Web/Contributors/GetById.cs:56` and `src/Clean.Architecture.Web/Contributors/GetById.cs:27`; and the update mapper and example at `src/Clean.Architecture.Web/Contributors/Update.cs:65` and `src/Clean.Architecture.Web/Contributors/Update.cs:29`.
- **Update response container** — no structural change is needed, but the `contributor` object is typed as `ContributorRecord` at `src/Clean.Architecture.Web/Contributors/Update.UpdateContributorResponse.cs:3-5`, so it inherits the new field.
- **Seed data** — change the first seeded row to `ContributorStatus.CoreTeam` at `src/Clean.Architecture.Infrastructure/Data/SeedData.cs:21` (leave the total count at `src/Clean.Architecture.Infrastructure/Data/SeedData.cs:7` unchanged) so a non-default status is available to tests.
- **Functional tests** — extend the list assertions at `tests/Clean.Architecture.FunctionalTests/ApiEndpoints/ContributorList.cs:14-18` and the get-by-id assertions at `tests/Clean.Architecture.FunctionalTests/ApiEndpoints/ContributorGetById.cs:15-18`. The record deserialization smoke tests at `tests/Clean.Architecture.FunctionalTests/SqlServerOnLinuxTests.cs:44-48` and `tests/Clean.Architecture.FunctionalTests/SqliteFallbackTests.cs:20-25` also validate that the expanded positional record deserializes correctly.

## Out of Scope

- Accepting `status` on create or update requests.
- Filtering, sorting, or grouping the list by status (a possible follow-up query parameter).
- A standalone `/Contributors/statuses` or enum-metadata endpoint.
- Any database migration, index, or schema change.
- Changing the default status for new contributors.

## Test Plan

1. Build the solution: `dotnet build Clean.Architecture.slnx`.
2. Run unit tests: `dotnet test tests/Clean.Architecture.UnitTests/Clean.Architecture.UnitTests.csproj`.
3. Run integration tests: `dotnet test tests/Clean.Architecture.IntegrationTests/Clean.Architecture.IntegrationTests.csproj`.
4. Run functional tests: `dotnet test tests/Clean.Architecture.FunctionalTests/Clean.Architecture.FunctionalTests.csproj` (uses SQL Server Testcontainers when Docker is available and falls back to SQLite otherwise).
5. New assertions:
   - List: the seeded contributor named `Ardalis` has `status == "CoreTeam"`, and every item's status is non-empty.
   - Get-by-id: contributor 1 returns `status == "CoreTeam"`; id 1000 still returns 404.
   - Update: after renaming contributor 1, the returned `contributor.status` is still `"CoreTeam"`.
6. Manual/API smoke check for `GET /Contributors` and `GET /Contributors/1` when running the Web project.

## Risks and Mitigations

- **Raw SQL column mismatch** — EF's `FromSqlRaw` composition will fail if `Status` is projected but absent from the SQL. Mitigation: update the `SELECT` list and verify on both SQL Server and SQLite functional tests (see `ListContributorsQueryService.cs:19`).
- **Positional record compile breaks** — adding a constructor parameter to `ContributorRecord` intentionally surfaces every construction site at compile time; update every construction site listed above rather than adding an optional overload.
- **Seed-data expectations** — changing contributor 1's seeded status must not change the row count or the existing name assertions. Keep `NUMBER_OF_CONTRIBUTORS` and seeded names unchanged.
- **Wire compatibility** — the change is additive; consumers that ignore unknown JSON properties are unaffected. Serialization follows the API's existing camelCase convention, producing `status`.
