# ADR-007: Use Markdown memory instead of a vector store

- Status: Proposed
- Date: 2026-11-12

## Context

Sessions lose context between runs. Repeating discovery costs tokens and produces
inconsistent decisions. Two families of solutions exist:

1. **Retrieval by similarity:** embeddings plus a vector database (for example ChromaDB in
   `nerv`). Adds an index, an embedding model, a rebuild step, and a new failure mode.
2. **Deterministic documentation:** plain Markdown, a catalog, and an index that the agent
   reads on demand (for example `operator-memory`). Adds discipline and curation.

The repository targets cost efficiency and low operational complexity. A vector store
requires a service or a local database, consumes embedding tokens, and can silently
retrieve stale or duplicated content. It also makes the injected context non-reproducible,
which conflicts with the repository's evidence requirements.

## Decision

Adopt **Markdown-first memory** under `.ote/memory/` with three partitions:

| Partition | Scope | Tracked in Git |
|---|---|---|
| `user/` | Reader preferences and reusable standards | No |
| `project/` | Repository decisions, constraints, conventions | Yes, when the project opts in |
| `shared/` | Knowledge published with the repository | Yes |

Memory loads through a bounded preamble plus a catalog that routes to deeper files. No
embeddings, no vector database, and no background service.

## Rationale

- Inspectable and editable with existing tools.
- Diffable in review, so a wrong memory can be corrected like code.
- Deterministic: the same files produce the same preamble.
- Token cost is bounded by a configured budget instead of by retrieval count.
- No additional infrastructure to install, secure, or back up.

## Consequences

- Curation is the maintenance cost. Entries need an owner, a date, a confidence value, and
  a TTL so stale knowledge expires.
- Search is lexical, not semantic. Users must phrase queries with repository vocabulary.
- Duplicate detection must run before writing.
- Secret scanning must run before writing, because memory is plain text.

## Mitigations

| Risk | Mitigation |
|---|---|
| Stale entries | 30-day TTL and `ote memory prune` |
| Duplicate entries | Normalized-title check before write |
| Secret leakage | Reject writes matching credential patterns |
| Context bloat | Hard byte and token budget on the preamble |
| Wrong injection | Partition precedence `project > user > shared` and explicit source links |

## Verification required before acceptance

- The preamble stays under the configured budget on the repository itself.
- `ote memory search` works with the lexical index.
- A planted secret is rejected with a non-zero exit code.
- Removing the memory directory leaves the repository valid.

## References

- `docs/decisions/ADR-005-cli-stack.md`
- `docs/cost-optimization/observability.md`
- https://github.com/mikeyobrien/ralph-orchestrator
