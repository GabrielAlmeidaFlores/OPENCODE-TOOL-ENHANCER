# Pilot Feature: Reverse Dependencies in `turbo ls <package>`

> **Status:** Experimental · **Last verified:** 2026-11-12 · **Evidence:** pilot output, structurally verified, not independently reviewed

## Proposal

`turbo ls <package>` currently shows a package's path, its `depends on` list, and
its tasks in human-readable output. The data model and GraphQL query already
fetch reverse dependencies (`dependents`), but the pretty printer never displays
them. Surface them as a `depended on by:` section so users can answer "what
breaks if I change this package?" without switching to JSON.

## Acceptance Criteria

1. `turbo ls <package>` pretty output includes a `depended on by:` line directly
   after the existing `depends on:` line.
2. The list is sorted, deduplicated, and excludes the root package (`//`) and the
   package itself, matching the JSON output.
3. An empty reverse-dependency set prints `<no packages>`, consistent with the
   existing empty `depends on` behavior.
4. `--output=json` output is unchanged, and existing snapshot/unit tests for
   `turbo ls` are updated to cover the new line.

## Evidence

- `PackageDetailsDisplay` already stores and serializes `dependents`
  (`crates/turborepo-cli/src/commands/ls.rs:85`), and the GraphQL query already
  requests `allDependents` (`crates/turborepo-cli/src/commands/ls.rs:38`).
- `parse_package_detail` already builds a sorted, filtered dependents list
  (`crates/turborepo-cli/src/commands/ls.rs:329-346`), so this change needs no
  extra repository queries.
- `print_package_detail` renders only `depends on` and tasks today
  (`crates/turborepo-cli/src/commands/ls.rs:420-451`); the new section is a
  presentation-only change, while `--output=json` continues to use serde via
  `print_repo_details` (`crates/turborepo-cli/src/commands/ls.rs:375-378`).
