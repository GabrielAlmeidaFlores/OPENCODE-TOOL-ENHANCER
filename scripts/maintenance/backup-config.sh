#!/usr/bin/env bash
# Back up OpenCode global config and project .opencode state.
set -euo pipefail

STAMP="$(date +%Y%m%d-%H%M%S)"
DEST="${1:-$HOME/.opencode-backups/$STAMP}"
mkdir -p "$DEST"

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
