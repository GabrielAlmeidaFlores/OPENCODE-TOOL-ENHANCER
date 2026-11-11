---
name: docs-sync
description: Keep documentation and commands aligned with code. Use after behavior, configuration, or CLI changes.
---

# Documentation Sync

## Steps

1. Find the docs that mention the changed behavior: `rg -n "<term>" docs README.md`.
2. Update the smallest set of pages.
3. Run every command you documented.
4. Check every external link resolves.
5. Update the changelog for user-visible changes.
6. Remove stale examples rather than annotating them as old.

## Rules

- Do not document unverified flags or options.
- Do not duplicate a reference; link to the canonical page.
- Explain the concept before the configuration.
- Keep examples copy-pasteable.
- Note compatibility constraints and deprecations explicitly.

## Output

Changed files, commands verified, links checked, and remaining gaps.
