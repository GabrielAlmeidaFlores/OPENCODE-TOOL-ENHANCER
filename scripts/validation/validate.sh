#!/usr/bin/env bash
# Name: Repository validation entry point
# Purpose: Checks required files, JSONC and YAML syntax, agent and skill frontmatter, provenance, git permission ordering, links, and shell syntax.
# Usage: ./scripts/validation/validate.sh [--links]
# Arguments: --links enables external link reachability checks.
# Environment: Requires bash and python3; uses opencode when available.
# Outputs: Prints check results and exits non-zero on failure.
# Side effects: Performs read-only checks; --links makes outbound HTTP requests.
# References: docs/validation-checklist.md, scripts/validation/validate_config.py
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT/scripts/lib/strings.sh"
cd "$ROOT"

echo "${SH_FILES}"
for f in README.md LICENSE CONTRIBUTING.md AGENTS.md \
         configs/opencode/opencode.jsonc configs/opencode/minimal.jsonc \
         configs/ralph/ralph.yml configs/ralph/hats/code-assist.yml; do
  [[ -f "$f" ]] || { echo "missing: $f"; exit 1; }
done

echo "${SH_JSONC_YAML_FRONTMATTER}"
python3 scripts/validation/validate_config.py "$@"

if command -v opencode >/dev/null 2>&1; then
  echo "${SH_OPENCODE}"
  opencode --version
  if opencode debug agents >/dev/null 2>&1; then
    echo "${SH_DEBUG_AGENTS_OK}"
  else
    echo "debug agents: skipped (needs project .opencode/agents)"
  fi
else
  echo "${SH_OPENCODE_NOT_FOUND_SKIPPING_CLI_CHECKS}"
fi

echo "${SH_SHELL_SYNTAX}"
for f in scripts/installation/*.sh scripts/maintenance/*.sh scripts/benchmarking/*.sh benchmarks/harness/*.sh skills/*/*.sh; do
  [[ -f "$f" ]] || continue
  bash -n "$f"
done

echo "${SH_OK}"
