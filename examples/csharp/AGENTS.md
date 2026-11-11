# AGENTS.md — C# example

## Commands

```bash
dotnet restore
dotnet build
dotnet test
```

Run `dotnet test` before declaring a task complete.

## Structure

- `Example/Program.cs` — request validation and file resolution
- `Example.Tests/ValidationTests.cs` — xunit tests

## Conventions

- Nullable reference types are enabled; do not suppress warnings without a reason.
- Use `record` types for request models.
- Keep validation messages stable and user-facing.

## Safety

Do not read `.env` files. Do not add NuGet packages without approval.
