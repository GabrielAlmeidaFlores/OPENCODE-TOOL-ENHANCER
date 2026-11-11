---
name: codebase-navigation
description: Find code with the cheapest sufficient tool before reading whole files. Use when locating symbols, callers, or implementations in a repository.
---

# Codebase Navigation

## Order of operations

1. **Native search** — `grep`/`rg` for exact strings, error messages, and config keys.
2. **File discovery** — `glob`/`rg --files` to narrow by name and extension.
3. **Structural search** — `ast-grep` when the shape matters more than the text.
4. **Symbol navigation** — Serena when a definition, reference, or implementation must be resolved semantically.
5. **Graph queries** — CodeGraph when the question is about callers, dependencies, or blast radius across files.
6. **Targeted read** — read the smallest line range that answers the question.

## Rules

- Do not read an entire large file to find one symbol.
- Do not run the same query twice with different tools.
- Stop searching when the evidence is sufficient; report what you did not inspect.
- Cite `file:line` for every claim.

## Examples

```bash
rg -n "class OrderService" --type ts
ast-grep -p 'if ($COND) { $BODY }' -l ts src/
```

Use Serena/CodeGraph through their MCP tools by name when available. If a server is not connected, fall back to the previous step instead of blocking.
