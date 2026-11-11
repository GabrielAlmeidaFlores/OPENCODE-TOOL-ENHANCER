#!/usr/bin/env bash
# Repository validation entry point.
# Usage: ./scripts/validation/validate.sh [--links]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "== files =="
for f in README.md LICENSE CONTRIBUTING.md AGENTS.md \
         configs/opencode/opencode.jsonc configs/opencode/minimal.jsonc \
         configs/ralph/ralph.yml configs/ralph/hats/code-assist.yml; do
  [[ -f "$f" ]] || { echo "missing: $f"; exit 1; }
done

echo "== jsonc / yaml / frontmatter =="
python3 scripts/validation/validate_config.py "$@"

if command -v opencode >/dev/null 2>&1; then
  echo "== opencode =="
  opencode --version
  if opencode debug agents >/dev/null 2>&1; then
    echo "debug agents: ok"
  else
    echo "debug agents: skipped (needs project .opencode/agents)"
  fi
else
  echo "opencode not found; skipping CLI checks"
fi

echo "== shell syntax =="
for f in scripts/installation/*.sh scripts/maintenance/*.sh scripts/benchmarking/*.sh benchmarks/harness/*.sh; do
  [[ -f "$f" ]] || continue
  bash -n "$f"
done

echo "OK"
