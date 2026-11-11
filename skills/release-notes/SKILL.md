---
name: release-notes
description: Produce release notes and a version decision from merged changes. Use when preparing a tag, changelog, or release.
---

# Release Notes

## Steps

1. Collect merged changes since the last tag: `git log <last>..HEAD --oneline`.
2. Classify: breaking, feature, fix, performance, security, documentation, internal.
3. Decide the semantic version: major for breaking, minor for features, patch for fixes.
4. Write user-facing notes: what changed, why it matters, and any action required.
5. List migration steps for breaking changes.
6. Verify the build and tests on the release commit.

## Rules

- Do not include internal refactors unless they affect users.
- Do not claim performance improvements without measurements.
- Security fixes must be described without exposing an exploit before users can upgrade.
- Link issues and pull requests.

## Output

Version, changelog section, migration notes, verification evidence, and rollback plan.
