---
name: db-migration
description: Plan safe, reversible database migrations. Use when changing schemas, backfilling data, or adding indexes.
---

# Database Migration

## Expand and contract

1. **Expand** — add nullable columns, new tables, or indexes without breaking old code.
2. **Migrate** — dual-write or backfill in bounded batches.
3. **Switch** — move reads to the new shape.
4. **Contract** — remove the old column or table after the deprecation window.

## Checklist

- Forward and rollback path for each step.
- Lock duration on large tables; use concurrent index creation where supported.
- Backfill batch size and resumability.
- Constraint validation strategy.
- Query plan for the new access pattern.
- Backup and restore rehearsal for destructive steps.

## Rules

- Never run destructive statements against a non-local database without human approval.
- Do not add an index without naming the query it serves.
- Do not change a column type without a backfill plan.
- Test the migration on a copy with production-like volume.

## Output

Migration steps, rollback steps, expected lock time, verification commands, and the exact approval required before running.
