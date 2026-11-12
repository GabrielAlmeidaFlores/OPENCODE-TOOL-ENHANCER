# Pilot Bug Report

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** pilot output, structurally verified, not independently reviewed

## Suspected bug

The `UseDbGeneratedIds` SQL Server migration corrupts the rename sequence used to rebuild `Contributors` with an IDENTITY column. It passes bracketed identifiers as the *new* name to `sp_rename` (`N'[Contributors_old]'`), but `sp_rename` treats `@newname` literally, so the table is renamed to a name that includes the brackets. The immediately following primary-key rename then references `Contributors_old` and fails to find the renamed object, aborting the migration. The same faulty pattern is duplicated in `Down`, so both upgrading an existing SQL Server database and rolling back the migration can fail even though the SQLite path succeeds. This means deployments that already have contributor rows cannot apply the migration that switches IDs to database-generated values.

## Proposed regression test

Add a SQL Server Testcontainers integration test (for example in `tests/Clean.Architecture.FunctionalTests/SqlServerOnLinuxTests.cs`) that migrates the database to the migration immediately preceding `20260424000000_UseDbGeneratedIds`, inserts a contributor, applies the latest migration, asserts the existing row survived and a newly inserted row received an IDENTITY-generated ID, then applies `Down` and asserts it completes without error. The test should assert migration success explicitly so the duplicate bracketed-name bug in both `Up` and `Down` is caught.

## Evidence

- `src/Clean.Architecture.Infrastructure/Data/Migrations/20260424000000_UseDbGeneratedIds.cs:17-18` — `Up` renames the table using `N'[Contributors_old]'` and then tries to rename `PK_Contributors` through `N'[Contributors_old].[PK_Contributors]'`, which cannot resolve the bracketed new name.
- `src/Clean.Architecture.Infrastructure/Data/Migrations/20260424000000_UseDbGeneratedIds.cs:53-54` — `Down` repeats the same bracketed `sp_rename` calls, so rollback fails for the same reason as the forward migration.
- `src/Clean.Architecture.Infrastructure/Data/Migrations/20260424000000_UseDbGeneratedIds.cs:13` and `:51` — the faulty SQL is gated to `Microsoft.EntityFrameworkCore.SqlServer`, so SQLite-based tests pass while real SQL Server deployments break.
