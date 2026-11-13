# ripgrep

> **Status:** Stable · **Last verified:** 2026-11-12 · **Evidence:** verified locally

Fast text search. The default for exact strings, error messages, and configuration keys.

- Repository: https://github.com/BurntSushi/ripgrep
- License: MIT / Unlicense
- Integration: CLI and OpenCode's built-in search

## Install

```bash
brew install ripgrep        # macOS
sudo apt install ripgrep    # Debian/Ubuntu
rg --version
```

## Usage

```bash
rg -n "OrderService" --type ts
rg -n "TODO|FIXME" -g '!node_modules' -g '!dist'
rg -n --hidden --glob '!.git' "api[_-]?key"
rg --files -g '*.cs' src/
```

## Strengths

- Fast, deterministic, no model tokens.
- Respects [`.gitignore`](https://github.com/GabrielAlmeidaFlores/ToolWright/blob/main/.gitignore) by default.
- Excellent for confirming whether a symbol name exists before deeper analysis.

## Limits

- No semantic understanding. Finds text, not symbols.
- Cannot answer "who calls this" or "what implements this interface".
- Regex over minified or generated files is noisy; exclude them.

## When not to use

- When you need a definition vs. a reference distinction.
- When the query is structural (use ast-grep) or dependency-related (use CodeGraph).

## Token implications

Search output can be large. Prefer `-n`, a path scope, and `--max-count`. Do not paste whole result sets into a prompt; select the relevant matches.
