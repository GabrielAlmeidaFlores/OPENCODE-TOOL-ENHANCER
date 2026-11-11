---
name: refactor-safely
description: Change structure without changing behavior. Use when extracting modules, renaming, or untangling dependencies.
---

# Refactor Safely

## Preconditions

- There is a test suite, or you add characterization tests first.
- The target behavior is understood and recorded.
- The refactor is separate from a feature change.

## Steps

1. Capture the current behavior with tests or golden outputs.
2. Make one mechanical change at a time.
3. Run the narrowest test after each change.
4. Keep public contracts stable unless the change is explicitly a contract change.
5. Commit or checkpoint before the next structural step.

## Rules

- Do not mix formatting with logic changes.
- Do not rename and move in the same step.
- Do not "clean up" unrelated code.
- If a test must change, explain why the behavior is unchanged.

## Output

Behavior preserved (evidence), steps taken, and any follow-up refactors deliberately deferred.
