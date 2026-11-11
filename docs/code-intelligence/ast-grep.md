# ast-grep

Structural search and rewrite over an abstract syntax tree. Use when the shape of the code matters more than the text.

- Repository: https://github.com/ast-grep/ast-grep
- Version used: 0.51.2
- License: MIT
- Integration: CLI (no MCP)

## Install

```bash
brew install ast-grep
# or
npm install --global @ast-grep/cli
ast-grep --version
```

## Usage

```bash
# Find a syntax shape
ast-grep -p 'if ($COND) { $BODY }' -l ts src/

# Find calls on a specific receiver
ast-grep -p '$OBJ.$METHOD($$$ARGS)' -l ts src/

# Rewrite, dry run first
ast-grep -p 'console.log($ARG)' -l ts -r 'logger.debug($ARG)' src/
```

`$NAME` matches one AST node; `$$$ARGS` matches zero or more.

## Project configuration

Create `.sgconfig.yml`:

```yaml
ruleDirs:
  - tools/ast-grep/rules
testConfigs:
  - testDir: tools/ast-grep/tests
```

Each rule is a YAML file with `id`, `language`, `rule`, `message`, and `severity`.

## Strengths

- Deterministic, fast, and language-aware.
- No model tokens; ideal for lint-style checks and mechanical rewrites.
- Handles patterns that regex cannot express safely.

## Limits

- Not a symbol resolver. It cannot follow imports or type hierarchies.
- Grammar coverage depends on the bundled tree-sitter parsers.
- Rewrites can change formatting; review the diff.

## When not to use

- For plain text or configuration changes (use `rg`).
- For "find references" or "go to definition" (use Serena).
- For cross-file dependency questions (use CodeGraph).

## Token implications

AST output is still text. Scope it by path and pattern, and pipe large results through a count first:

```bash
ast-grep -p '$A && $A()' -l ts src/ --json=stream | wc -l
```
