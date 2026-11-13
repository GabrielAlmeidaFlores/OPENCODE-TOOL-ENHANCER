#!/usr/bin/env bash
# Name: OpenCode and project configuration backup
# Purpose: Archives the global OpenCode configuration and the project's .opencode and .ralph directories, or only the project directories with --project-only.
# Usage: ./scripts/maintenance/backup-config.sh [DESTINATION] [--project-only]
# Arguments: $1 is the destination directory; --project-only skips the global configuration. The destination defaults to ~/.opencode-backups/<timestamp>.
# Environment: Requires bash and tar.
# Outputs: Prints the backup directory and each archived path.
# Side effects: Creates archives under the destination directory.
# References: docs/installation/opencode.md, docs/troubleshooting/README.md
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT/scripts/lib/strings.sh"
set -euo pipefail

PROJECT_ONLY=0
DEST="${SH_TEXT}"
for argument in "$@"; do
  case "$argument" in
    --project-only) PROJECT_ONLY=1 ;;
    *) DEST="$argument" ;;
  esac
done

STAMP="$(date +%Y%m%d-%H%M%S)"
DEST="${DEST:-$HOME/.opencode-backups/$STAMP}"
mkdir -p "$DEST"

# Function: backup_dir
# Description: Archives one directory when it exists.
# Arguments: $1 is the source directory, $2 is the archive base name.
# Returns: Zero on success or when the source is missing.
# Side effects: Writes a .tar.gz archive to DEST.
backup_dir() {
  local src="$1" name="$2"
  if [[ -d "$src" ]]; then
    tar -czf "$DEST/$name.tar.gz" -C "$(dirname "$src")" "$(basename "$src")"
    echo "backed up $src -> $DEST/$name.tar.gz"
  else
    echo "skip (missing): $src"
  fi
}

if [[ "$PROJECT_ONLY" == "0" ]]; then
  backup_dir "$HOME/.config/opencode" "${SH_GLOBAL_CONFIG}"
fi
backup_dir "$PWD/.opencode" "${SH_PROJECT_OPENCODE}"
backup_dir "$PWD/.ralph" "${SH_PROJECT_RALPH}"

echo "backup directory: $DEST"
