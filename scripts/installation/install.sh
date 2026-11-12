#!/usr/bin/env bash
# Name: Selective installer
# Purpose: Installs the repository's OpenCode, agent, command, skill, and Ralph configuration into a target project, and optionally installs the external tool binaries.
# Usage: ./scripts/installation/install.sh [--check|--dry-run|--apply] [--all|--only LIST] [--target DIR] [--clean]
# Arguments: --check prints status, --dry-run prints actions, --apply executes them, --only selects components, --target selects the destination, --clean backs up and removes managed directories first.
# Environment: Requires bash, git, node, python3, and ripgrep for status checks. Tool installation uses brew, uv, or npm when available.
# Outputs: Prints planned or executed actions, a backup path, and verification commands.
# Side effects: With --apply, writes into TARGET/.opencode and TARGET/.ralph, may install global tools, and never edits ~/.config/opencode.
# References: docs/installation/opencode.md, docs/installation/code-intelligence.md, docs/installation/ralph.md
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MODE="check"
ONLY=""
TARGET="$ROOT"
CLEAN=0

# Function: usage
# Description: Prints the command-line options.
# Arguments: None.
# Returns: None.
# Side effects: Writes to standard output.
usage() {
  cat <<'EOF'
Options:
  --check              Print status only (default)
  --dry-run            Print planned actions without executing
  --apply              Execute selected actions
  --all                Select all components
  --only LIST          Comma-separated: opencode,agents,commands,skills,ralph,plugin,ast-grep,serena,codegraph
  --target DIR         Project directory for .opencode files (default: repo root)
  --clean              Back up and remove existing .opencode agents/commands/skills before copying
  -h, --help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --check) MODE="check"; shift ;;
    --dry-run) MODE="dry-run"; shift ;;
    --apply) MODE="apply"; shift ;;
    --all) ONLY="opencode,agents,commands,skills,ralph,ast-grep,serena,codegraph"; shift ;;
    --only) ONLY="${2:-}"; shift 2 ;;
    --target) TARGET="${2:-}"; shift 2 ;;
    --clean) CLEAN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1"; usage; exit 2 ;;
  esac
done

if [[ -z "$ONLY" && "$MODE" != "check" ]]; then
  echo "Select components with --all or --only. Refusing to guess."
  exit 2
fi

# Function: has
# Description: Reports whether a command exists on PATH.
# Arguments: $1 is the command name.
# Returns: Zero when the command exists, non-zero otherwise.
# Side effects: None.
has() { command -v "$1" >/dev/null 2>&1; }

# Function: selected
# Description: Reports whether a component was selected by --only or --all.
# Arguments: $1 is the component name.
# Returns: Zero when selected, non-zero otherwise.
# Side effects: None.
selected() { [[ ",$ONLY," == *",$1,"* ]]; }

# Function: run
# Description: Executes a command in apply mode or prints it in dry-run mode.
# Arguments: The command and its arguments.
# Returns: The command's exit status in apply mode, zero otherwise.
# Side effects: May execute the supplied command.
run() {
  if [[ "$MODE" == "apply" ]]; then
    "$@"
  else
    printf '  would run: %s\n' "$*"
  fi
}

echo "mode=$MODE target=$TARGET"

echo "== dependencies =="
for c in git node python3 rg; do
  if has "$c"; then printf '  ok   %-10s %s\n' "$c" "$(command -v "$c")"; else printf '  MISS %-10s\n' "$c"; fi
done
printf '  info opencode   %s\n' "$(opencode --version 2>/dev/null || echo 'not installed')"
printf '  info ralph      %s\n' "$(ralph --version 2>/dev/null || echo 'not installed')"
printf '  info ast-grep   %s\n' "$(ast-grep --version 2>/dev/null | head -1 || echo 'not installed')"
printf '  info serena     %s\n' "$(serena --version 2>/dev/null || echo 'not installed')"
printf '  info codegraph  %s\n' "$(codegraph --version 2>/dev/null || echo 'not installed')"

if [[ "$MODE" == "check" ]]; then
  echo "check complete. Use --dry-run or --apply."
  exit 0
fi

STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="$TARGET/.opencode-backup-$STAMP"
if [[ "$MODE" == "apply" ]]; then
  mkdir -p "$BACKUP"
fi

# Function: clean_dir
# Description: Backs up and removes a managed directory when --clean is active.
# Arguments: $1 is the directory path.
# Returns: Zero on success.
# Side effects: Copies the directory into the backup path and deletes the original in apply mode.
clean_dir() {
  local dir="$1"
  if [[ ! -d "$dir" ]]; then
    return 0
  fi
  if [[ "$MODE" == "apply" ]]; then
    mkdir -p "$BACKUP"
    cp -R "$dir" "$BACKUP/$(basename "$dir")"
    rm -rf "$dir"
    echo "  cleaned (backed up): $dir"
  else
    echo "  would clean: $dir"
  fi
}

# Function: copy_file
# Description: Copies a file and backs up an existing destination in apply mode.
# Arguments: $1 is the source path, $2 is the destination path.
# Returns: Zero on success.
# Side effects: May overwrite the destination and write a backup copy.
copy_file() {
  local src="$1" dst="$2"
  if [[ -f "$dst" && "$MODE" == "apply" ]]; then
    mkdir -p "$(dirname "$BACKUP/${dst#"$TARGET"/}")"
    cp "$dst" "$BACKUP/${dst#"$TARGET"/}"
  fi
  run cp "$src" "$dst"
}

# Function: copy_dir
# Description: Copies a directory tree and backs up an existing destination in apply mode.
# Arguments: $1 is the source directory, $2 is the destination directory.
# Returns: Zero on success.
# Side effects: May overwrite the destination and write a backup copy.
copy_dir() {
  local src="$1" dst="$2"
  if [[ -d "$dst" && "$MODE" == "apply" ]]; then
    mkdir -p "$BACKUP/${dst#"$TARGET"/}"
    cp -R "$dst/." "$BACKUP/${dst#"$TARGET"/}/"
  fi
  run mkdir -p "$dst"
  run cp -R "$src/." "$dst/"
}

if [[ "$CLEAN" == "1" ]]; then
  echo "== clean managed directories =="
  if selected agents; then
    clean_dir "$TARGET/.opencode/agents"
  fi
  if selected commands; then
    clean_dir "$TARGET/.opencode/commands"
  fi
  if selected skills; then
    clean_dir "$TARGET/.opencode/skills"
  fi
  if selected plugin; then
  echo "== opencode plugin =="
  run mkdir -p "$TARGET/.opencode/plugins"
  copy_file "$ROOT/configs/opencode/plugins/ote-memory.js" "$TARGET/.opencode/plugins/ote-memory.js"
fi

if selected ralph; then
    clean_dir "$TARGET/.ralph/hats"
  fi
fi

if selected opencode; then
  echo "== opencode config =="
  run mkdir -p "$TARGET/.opencode/agents" "$TARGET/.opencode/commands" "$TARGET/.opencode/skills"
  copy_file "$ROOT/configs/opencode/opencode.jsonc" "$TARGET/.opencode/opencode.jsonc"
fi

if selected agents; then
  echo "== agents =="
  run mkdir -p "$TARGET/.opencode/agents"
  for f in "$ROOT"/agents/*/AGENT.md; do
    role="$(basename "$(dirname "$f")")"
    copy_file "$f" "$TARGET/.opencode/agents/$role.md"
  done
fi

if selected commands; then
  echo "== commands =="
  run mkdir -p "$TARGET/.opencode/commands"
  for f in "$ROOT"/commands/*.md; do
    copy_file "$f" "$TARGET/.opencode/commands/$(basename "$f")"
  done
fi

if selected skills; then
  echo "== skills =="
  run mkdir -p "$TARGET/.opencode/skills"
  for d in "$ROOT"/skills/*/; do
    name="$(basename "$d")"
    copy_dir "$d" "$TARGET/.opencode/skills/$name"
  done
fi

if selected plugin; then
  echo "== opencode plugin =="
  run mkdir -p "$TARGET/.opencode/plugins"
  copy_file "$ROOT/configs/opencode/plugins/ote-memory.js" "$TARGET/.opencode/plugins/ote-memory.js"
fi

if selected ralph; then
  echo "== ralph configs =="
  run mkdir -p "$TARGET/.ralph"
  copy_file "$ROOT/configs/ralph/ralph.yml" "$TARGET/.ralph/ralph.yml"
  run mkdir -p "$TARGET/.ralph/hats"
  for f in "$ROOT"/configs/ralph/hats/*.yml; do
    copy_file "$f" "$TARGET/.ralph/hats/$(basename "$f")"
  done
fi

if selected ast-grep; then
  echo "== ast-grep =="
  if has ast-grep; then
    echo "  already installed"
  elif has brew; then
    run brew install ast-grep
  else
    echo "  install manually: npm install --global @ast-grep/cli"
  fi
fi

if selected serena; then
  echo "== serena =="
  if has serena; then
    echo "  already installed"
  elif has uv; then
    run uv tool install -p 3.13 serena-agent
  else
    echo "  install uv first: https://docs.astral.sh/uv/getting-started/installation/"
  fi
fi

if selected codegraph; then
  echo "== codegraph =="
  if has codegraph; then
    echo "  already installed"
  else
    echo "  install manually:"
    echo "    curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh"
    echo "  note: installer downloads and executes a remote script; review it first."
  fi
fi

if [[ "$MODE" == "apply" ]]; then
  echo "backup: $BACKUP"
  echo "verify: opencode debug config && opencode debug agents && opencode mcp list"
  echo "rollback: copy files back from $BACKUP"
fi
