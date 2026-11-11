# C# Example

A minimal .NET 8 example used by the benchmark tasks.

## Run

```bash
dotnet restore
dotnet test
```

## Try an agent

```bash
opencode run --agent coordinator "Add a maximum name length of 100 to Validator and cover it with a test"
opencode run --agent security-reviewer "Review FileResolver.Resolve for path traversal"
```

The example contains a deliberate path traversal in `FileResolver`.
