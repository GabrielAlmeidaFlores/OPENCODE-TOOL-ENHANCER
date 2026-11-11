# TypeScript Example

A minimal repository used by the benchmark tasks. It contains deliberate weaknesses for the tasks to fix:

- duplicated pricing logic
- an N+1 order loader
- a path traversal in file resolution
- incomplete input validation

## Run

```bash
npm install
npm test
```

## Try an agent

```bash
opencode run --agent coordinator "Add validation to validateCreateUser for a required age and cover it with tests"
opencode run --agent code-reviewer "Review src/files.ts for security issues"
```

## Note

`npm test` compiles to `dist/` and runs Node's built-in test runner. No test framework dependency is required.
