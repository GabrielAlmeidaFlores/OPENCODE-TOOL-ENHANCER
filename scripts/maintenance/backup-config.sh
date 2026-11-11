#!/usr/bin/env bash
# Name: OpenCode and project configuration backup
# Purpose: Archives the global OpenCode configuration and the project's .opencode and .ralph directories.
# Usage: ./scripts/maintenance/backup-config.sh [DESTINATION]
# Arguments: $1 is the destination directory; defaults to ~/.opencode-backups/<timestamp>.
# Environment: Requires bash and tar.
# Outputs: Prints the backup directory and each archived path.
# Side effects: Creates archives under the destination directory.
# References: docs/installation/opencode.md, docs/troubleshooting/README.md
set -euo pipefail

STAMP="$(date +%Y%m%d-%H%M%S)"
DEST="${1:-$HOME/.opencode-backups/$STAMP}"
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

backup_dir "$HOME/.config/opencode" "global-config"
backup_dir "$PWD/.opencode" "project-opencode"
backup_dir "$PWD/.ralph" "project-ralph"

echo "backup directory: $DEST"
