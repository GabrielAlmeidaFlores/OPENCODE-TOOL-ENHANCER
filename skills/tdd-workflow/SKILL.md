---
name: tdd-workflow
description: Red-green-refactor workflow with real failing tests and evidence. Use when adding behavior or fixing a defect that can be captured by a test.
---

# TDD Workflow

## Steps

1. **Write the test first.** It must fail for the intended reason. Run it and capture the failure.
2. **Implement the smallest change** that makes it pass.
3. **Run the test again.** If it passes for the wrong reason, fix the test.
4. **Refactor** with the test green.
5. **Run the narrow suite, then the full suite.**

## Rules

- A test that passes before the change proves nothing.
- Do not mock the behavior under test.
- Assert on observable behavior, not internal calls.
- One behavior per test; name it after the behavior.
- No sleeps, no retries to hide flakiness.
- If the defect cannot be reproduced, stop and report what is missing.

## Evidence to return

```
Added: <test file:line>
Before fix: <command> -> <failure summary>
After fix:  <command> -> <pass summary>
Full suite: <command> -> <result>
```
