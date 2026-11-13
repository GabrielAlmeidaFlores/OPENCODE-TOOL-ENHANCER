# Project Memory

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally and in CI run 43277080347

Memory is plain Markdown under `.toolwright/memory/`. There are no embeddings, no vector database, and no background service.

## Layout

```text
.toolwright/memory/
├── catalog.md      generated index
├── project/        repository decisions and constraints (tracked)
├── shared/         published knowledge (tracked)
└── user/           local preferences (gitignored)
```

Precedence for the generated preamble is `project > user > shared`.

## Entry format

```markdown
---
type: decision
title: Use expand-and-contract migrations
created: 2026-11-12
source: docs/decisions/ADR-001.md
confidence: 0.9
expires: 2026-12-12
links: [docs/decisions/ADR-001.md]
---

Replace columns in expand and contract steps so old and new code can run
against the same schema during a rolling deploy.
```

Allowed types: `decision`, `constraint`, `convention`, `failure`, `question`.

## Commands

```bash
toolwright memory add "Use expand-and-contract migrations" --type constraint --source docs/decisions/ADR-001.md
toolwright memory add "Flaky auth test" --type failure --ttl-days 7
toolwright memory search migrations
toolwright memory search --type constraint access
toolwright memory prune
toolwright memory prune --apply --yes
toolwright memory export
toolwright memory export --format json
toolwright memory preamble --budget 1500
```

| Command | Behavior |
|---|---|
| `add` | Writes one entry, rejects duplicate titles per scope, and refuses credential patterns |
| `search` | Lexical match over title, body, source, and type; optional type and scope filters |
| `prune` | Lists expired entries; `--apply --yes` deletes them and regenerates the catalog |
| `export` | Markdown or JSON snapshot |
| `preamble` | Deterministic, token-bounded summary ordered by scope precedence |

## Guarantees

- **No embeddings.** Search is lexical and deterministic.
- **Bounded context.** The preamble stops at the configured token budget (estimated at four characters per token).
- **Expiry.** Entries expire after `ttl_days` and are excluded from the preamble. Default: 30 days.
- **Secrets.** Candidate AWS keys, GitHub tokens, OpenAI keys, private keys, and generic `api_key`/`token`/`password` assignments are rejected before writing.
- **Deduplication.** A normalized title match in the same scope is refused unless `--force` is used.
- **Git.** `project/` and `shared/` are tracked; `user/` is ignored. `catalog.md` is generated.

## Configuration

```toml
[memory]
token_budget = 2000
ttl_days = 30
```

## Using memory with OpenCode

Reference [`.toolwright/memory/catalog.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/.toolwright/memory/catalog.md) from the project [`AGENTS.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/AGENTS.md), or load the preamble on demand:

```bash
toolwright memory preamble
```

Session-start injection through an OpenCode plugin is deferred to a later phase. The CLI is the stable interface.

## Design reference

The three-partition Markdown-first model follows `aerovato/operator-memory` (BSD-3-Clause): deterministic loading, catalog routing, and no retrieval by similarity. The implementation is original Python; see [`docs/provenance/registry.yml`](../provenance/registry.yml) entry `memory-and-specs`.

## References

- [`docs/specs/README.md`](../specs/README.md)
- [`docs/decisions/ADR-007-memory-without-rag.md`](../decisions/ADR-007-memory-without-rag.md)
- [`.toolwright/memory/README.md`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/.toolwright/memory/README.md)
