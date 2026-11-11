#!/usr/bin/env bash
# Collect OpenCode usage statistics for the current project.
set -euo pipefail

OUT="${1:-opencode-stats-$(date +%Y%m%d-%H%M%S).json}"
if ! command -v opencode >/dev/null 2>&1; then
  echo "opencode not found"
  exit 2
fi

opencode stats --json --cost --project . > "$OUT"
echo "wrote $OUT"
python3 - "$OUT" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
print(json.dumps(d, indent=2)[:2000])
PY
