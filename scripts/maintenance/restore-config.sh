#!/usr/bin/env bash
# Name: Configuration restore
# Purpose: Restores archives produced by backup-config.sh.
# Usage: ./scripts/maintenance/restore-config.sh <backup-dir> [global|project]
# Arguments: $1 is the backup directory; $2 selects the global or project scope and defaults to project.
# Environment: Requires bash and tar.
# Outputs: Prints each restored archive and the destination.
# Side effects: Overwrites files under ~/.config or the current project directory.
# References: scripts/maintenance/backup-config.sh, docs/troubleshooting/README.md
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT/scripts/lib/strings.sh"
set -euo pipefail

SRC="${1:-}"
SCOPE="${2:-project}"
if [[ -z "$SRC" || ! -d "$SRC" ]]; then
  echo "usage: $0 <backup-dir> [global|project]"
  exit 2
fi

# Function: restore
# Description: Extracts one archive into a destination directory.
# Arguments: $1 is the archive path, $2 is the destination directory.
# Returns: Zero on success or when the archive is missing.
# Side effects: Writes extracted files under the destination.
restore() {
  local archive="$1" dest="$2"
  [[ -f "$archive" ]] || { echo "missing: $archive"; return 0; }
  echo "restoring $archive -> $dest"
  tar -xzf "$archive" -C "$dest"
}

if [[ "$SCOPE" == "${SH_GLOBAL}" ]]; then
  restore "$SRC/global-config.tar.gz" "$HOME/.config"
else
  restore "$SRC/project-opencode.tar.gz" "$PWD"
  restore "$SRC/project-ralph.tar.gz" "$PWD"
fi

echo "${SH_RESTORE_COMPLETE_RE_RUN_OPENCODE_DEBUG_CONFIG_TO_V}"
