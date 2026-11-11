#!/usr/bin/env bash
# Name: OpenCode statistics collector
# Purpose: Captures token, cost, model, and tool statistics for the current project.
# Usage: ./scripts/benchmarking/collect_stats.sh [OUTPUT]
# Arguments: $1 is the output JSON path; defaults to opencode-stats-<timestamp>.json.
# Environment: Requires bash, opencode, and python3.
# Outputs: Writes a JSON file and prints a truncated preview.
# Side effects: Creates the output file.
# References: docs/benchmarks/methodology.md, https://opencode.ai/docs/cli
set -euo pipefail

OUT="${1:-opencode-stats-$(date +%Y%m%d-%H%M%S).json}"
if ! command -v opencode >/dev/null 2>&1; then
  echo "opencode not found"
  exit 2
fi

opencode stats --json --cost --project . > "$OUT"
echo "wrote $OUT"
python3 - "$OUT" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    data = json.load(handle)
print(json.dumps(data, indent=2)[:2000])
PY
