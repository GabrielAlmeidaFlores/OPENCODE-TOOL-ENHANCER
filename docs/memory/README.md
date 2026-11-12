# Project Memory

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally and in CI run 43275405166

Memory is plain Markdown under `.ote/memory/`. There are no embeddings, no vector database, and no background service.

## Layout

```text
.ote/memory/
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
ote memory add "Use expand-and-contract migrations" --type constraint --source docs/decisions/ADR-001.md
ote memory add "Flaky auth test" --type failure --ttl-days 7
ote memory search migrations
ote memory search --type constraint access
ote memory prune
ote memory prune --apply --yes
ote memory export
ote memory export --format json
ote memory preamble --budget 1500
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

Reference `.ote/memory/catalog.md` from the project `AGENTS.md`, or load the preamble on demand:

```bash
ote memory preamble
```

Session-start injection through an OpenCode plugin is deferred to a later phase. The CLI is the stable interface.

## Design reference

The three-partition Markdown-first model follows `aerovato/operator-memory` (BSD-3-Clause): deterministic loading, catalog routing, and no retrieval by similarity. The implementation is original Python; see `docs/provenance/registry.yml` entry `memory-and-specs`.

## References

- `docs/specs/README.md`
- `docs/decisions/ADR-007-memory-without-rag.md`
- `.ote/memory/README.md`
