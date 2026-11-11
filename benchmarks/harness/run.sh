#!/usr/bin/env bash
# Benchmark runner. Records artifacts; does not publish results.
#
# Usage:
#   ./benchmarks/harness/run.sh --arm baseline  --task benchmarks/tasks/ts-validation.json
#   ./benchmarks/harness/run.sh --arm optimized --task benchmarks/tasks/ts-validation.json --run-id opt-1
#
# Requires: opencode (V2), python3, git. Runs with --auto because the harness is
# non-interactive. Use a disposable checkout.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ARM=""
TASK=""
RUN_ID=""
DRY=0

usage() {
  echo "usage: $0 --arm baseline|optimized --task <file.json> [--run-id ID] [--dry-run]"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --arm) ARM="${2:-}"; shift 2 ;;
    --task) TASK="${2:-}"; shift 2 ;;
    --run-id) RUN_ID="${2:-}"; shift 2 ;;
    --dry-run) DRY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown: $1"; usage; exit 2 ;;
  esac
done

[[ -n "$ARM" && -n "$TASK" ]] || { usage; exit 2; }
[[ -f "$TASK" ]] || { echo "task not found: $TASK"; exit 2; }
command -v opencode >/dev/null || { echo "opencode not found"; exit 2; }
command -v python3 >/dev/null || { echo "python3 not found"; exit 2; }

read -r TASK_ID PROMPT VERIFY MAX_WALL < <(python3 - "$TASK" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
print(d["id"], d["prompt"].replace("\n"," "), d["verification"], d.get("max_wall_time_seconds", 900))
PY
)

RUN_ID="${RUN_ID:-$ARM-$TASK_ID-$(date +%Y%m%d-%H%M%S)}"
OUT="$ROOT/benchmarks/results/$RUN_ID"
if [[ -e "$OUT" ]]; then
  echo "refusing to overwrite: $OUT"
  exit 2
fi

case "$ARM" in
  baseline)
    CONFIG="$ROOT/benchmarks/baseline/opencode.json"
    AGENT="build"
    ;;
  optimized)
    CONFIG="$ROOT/configs/opencode/opencode.jsonc"
    AGENT="coordinator"
    if [[ ! -f "$ROOT/.opencode/agents/coordinator.md" ]]; then
      echo "optimized arm requires .opencode/agents/coordinator.md (run the installer)"
      exit 2
    fi
    ;;
  *) echo "unknown arm: $ARM"; exit 2 ;;
esac

COMMIT="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo unknown)"
MODEL="${OPENCODE_BENCH_MODEL:-user-selected}"

echo "arm=$ARM task=$TASK_ID run=$RUN_ID"
echo "config=$CONFIG agent=$AGENT commit=$COMMIT max_wall=${MAX_WALL}s"

if [[ "$DRY" == "1" ]]; then
  echo "would run: OPENCODE_CONFIG=$CONFIG opencode run --agent $AGENT --auto --format json <prompt>"
  exit 0
fi

mkdir -p "$OUT"

python3 - "$OUT/meta.json" "$RUN_ID" "$ARM" "$TASK" "$TASK_ID" "$COMMIT" "$MODEL" "$AGENT" "$MAX_WALL" <<'PY'
import json,sys,datetime
out,run_id,arm,task,task_id,commit,model,agent,max_wall=sys.argv[1:]
json.dump({
  "run_id": run_id,
  "arm": arm,
  "task_file": task,
  "task_id": task_id,
  "commit": commit,
  "model": model,
  "agent": agent,
  "max_wall_time_seconds": int(max_wall),
  "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
  "opencode_version": __import__("subprocess").run(["opencode","--version"],capture_output=True,text=True).stdout.strip(),
}, open(out,"w"), indent=2)
PY

START=$(date +%s)
set +e
OPENCODE_CONFIG="$CONFIG" opencode run --agent "$AGENT" --auto --format json "$PROMPT" \
  > "$OUT/session.jsonl" 2> "$OUT/session.err"
RUN_RC=$?
set -e
END=$(date +%s)

set +e
opencode stats --json --cost --project . > "$OUT/stats.json" 2> "$OUT/stats.err"
STATS_RC=$?

SID="$(python3 - "$OUT/session.jsonl" <<'PY2'
import re,sys
try:
    text=open(sys.argv[1],encoding="utf-8",errors="ignore").read()
except FileNotFoundError:
    text=""
ids=re.findall(r"ses_[A-Za-z0-9]+", text)
print(ids[-1] if ids else "")
PY2
)"
if [[ -n "$SID" ]]; then
  opencode session export --sanitize "$SID" > "$OUT/export.json" 2> "$OUT/export.err"
  EXPORT_RC=$?
else
  echo "no session id found in session.jsonl; export skipped" > "$OUT/export.err"
  : > "$OUT/export.json"
  EXPORT_RC=0
fi

bash -lc "$VERIFY" > "$OUT/verification.log" 2>&1
VERIFY_RC=$?
set -e

python3 - "$OUT/meta.json" "$RUN_RC" "$STATS_RC" "$EXPORT_RC" "$VERIFY_RC" "$START" "$END" <<'PY'
import json,sys,datetime
p,run_rc,stats_rc,export_rc,verify_rc,start,end=sys.argv[1:]
d=json.load(open(p))
d.update({
  "run_exit": int(run_rc),
  "stats_exit": int(stats_rc),
  "export_exit": int(export_rc),
  "verification_exit": int(verify_rc),
  "wall_time_seconds": int(end)-int(start),
  "finished_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
})
json.dump(d, open(p,"w"), indent=2)
PY

cat > "$OUT/notes.md" <<EOF
# $RUN_ID

- arm: $ARM
- task: $TASK_ID
- agent: $AGENT
- run exit: $RUN_RC
- verification exit: $VERIFY_RC
- wall time: $((END-START))s

## Fill in

- correctness (tests + rubric):
- rework / follow-up prompts:
- human interventions:
- residual risks:
EOF

echo "artifacts: $OUT"
echo "run_exit=$RUN_RC verification_exit=$VERIFY_RC wall=$((END-START))s"
[[ "$VERIFY_RC" == "0" ]] || echo "VERIFICATION FAILED"
