#!/usr/bin/env bash
# Restore a backup produced by backup-config.sh.
# Usage: ./scripts/maintenance/restore-config.sh <backup-dir> [global|project]
set -euo pipefail

SRC="${1:-}"
SCOPE="${2:-project}"
if [[ -z "$SRC" || ! -d "$SRC" ]]; then
  echo "usage: $0 <backup-dir> [global|project]"
  exit 2
fi

restore() {
  local archive="$1" dest="$2"
  [[ -f "$archive" ]] || { echo "missing: $archive"; return 0; }
  echo "restoring $archive -> $dest"
  tar -xzf "$archive" -C "$dest"
}

if [[ "$SCOPE" == "global" ]]; then
  restore "$SRC/global-config.tar.gz" "$HOME/.config"
else
  restore "$SRC/project-opencode.tar.gz" "$PWD"
  restore "$SRC/project-ralph.tar.gz" "$PWD"
fi

echo "restore complete. Re-run opencode debug config to verify."
