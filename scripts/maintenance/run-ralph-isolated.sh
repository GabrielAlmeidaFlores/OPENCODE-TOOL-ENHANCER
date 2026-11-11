#!/usr/bin/env bash
# Name: Isolated Ralph runner
# Purpose: Runs Ralph in a separate disposable clone so its landing commit never touches the working repository, then exports the resulting changes as a patch that can be applied unstaged.
# Usage: ./scripts/maintenance/run-ralph-isolated.sh [--dry-run] [--apply] [--cleanup] -- <ralph run arguments>
# Arguments: --dry-run prints the plan, --apply applies the exported patch to the current checkout without staging, --keep keeps the temporary clone, --cleanup removes it after the run.
# Environment: Requires bash, git, tar, and ralph on PATH.
# Outputs: Prints the temporary clone path and the exported patch path.
# Side effects: Creates a temporary clone, creates a baseline commit inside that clone, runs Ralph, writes a patch under .ralph-isolated, and optionally applies the patch to the current checkout.
# References: docs/orchestration/ralph.md, AGENTS.md Section 2B
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DRY=0
APPLY=0
CLEANUP=0
RALPH_ARGS=()

# Function: usage
# Description: Prints the command-line usage.
# Arguments: None.
# Returns: None.
# Side effects: Writes to standard output.
usage() {
  echo "usage: $0 [--dry-run] [--apply] [--cleanup] -- <ralph run arguments>"
  echo "example: $0 -- -c configs/ralph/ralph.yml -H configs/ralph/hats/research.yml -p \"Research <question>\""
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY=1; shift ;;
    --apply) APPLY=1; shift ;;
    --cleanup) CLEANUP=1; shift ;;
    -h|--help) usage; exit 0 ;;
    --) shift; RALPH_ARGS=("$@"); break ;;
    *) echo "unknown option: $1"; usage; exit 2 ;;
  esac
done

if [[ ${#RALPH_ARGS[@]} -eq 0 ]]; then
  echo "missing Ralph arguments"
  usage
  exit 2
fi

for command in git tar ralph; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "required command not found: $command"
    exit 2
  fi
done

STAMP="$(date +%Y%m%d-%H%M%S)"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/ralph-isolated.XXXXXX")"
CLONE="$TMP/repo"
PATCH_DIR="$ROOT/.ralph-isolated"
PATCH="$PATCH_DIR/$STAMP.patch"

if [[ "$DRY" == "1" ]]; then
  echo "would copy the working tree to: $CLONE"
  echo "would create a baseline commit inside the clone"
  echo "would run: ralph run ${RALPH_ARGS[*]}"
  echo "would write patch: $PATCH"
  [[ "$APPLY" == "1" ]] && echo "would apply the patch unstaged to: $ROOT"
  exit 0
fi

mkdir -p "$CLONE" "$PATCH_DIR"
tar -C "$ROOT" \
  --exclude='./.git' \
  --exclude='./.ralph/agent' \
  --exclude='./.ralph-isolated' \
  --exclude='./.codegraph' \
  --exclude='./node_modules' \
  --exclude='./.opencode/node_modules' \
  --exclude='./examples/csharp/bin' \
  --exclude='./examples/csharp/obj' \
  -cf - . | tar -C "$CLONE" -xf -

git -C "$CLONE" init -q
git -C "$CLONE" add -A
git -C "$CLONE" -c user.name="Ralph Isolated" -c user.email="ralph@example.invalid" \
  commit -qm "baseline for isolated Ralph run"
BASE="$(git -C "$CLONE" rev-parse HEAD)"

set +e
(
  cd "$CLONE"
  ralph run "${RALPH_ARGS[@]}"
)
RALPH_RC=$?
set -e

git -C "$CLONE" diff "$BASE" HEAD --binary > "$PATCH"
git -C "$CLONE" diff --binary >> "$PATCH"

echo "ralph exit: $RALPH_RC"
echo "clone: $CLONE"
echo "patch: $PATCH"

if [[ "$APPLY" == "1" ]]; then
  git -C "$ROOT" apply --binary "$PATCH"
  echo "applied patch unstaged to: $ROOT"
fi

if [[ "$CLEANUP" == "1" ]]; then
  rm -rf "$TMP"
  echo "removed clone: $TMP"
else
  echo "clone retained for inspection: $CLONE"
fi

exit "$RALPH_RC"
