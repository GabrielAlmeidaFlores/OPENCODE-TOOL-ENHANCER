#!/usr/bin/env bash
# shellcheck disable=SC2059  # format strings are named constants
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
source "$ROOT/scripts/lib/strings.sh"
MODE="$TW_MODE_CHECK"
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
    --check) MODE="$TW_MODE_CHECK"; shift ;;
    --dry-run) MODE="$TW_MODE_DRY_RUN"; shift ;;
    --apply) MODE="$TW_MODE_APPLY"; shift ;;
    --all) ONLY="${SH_OPENCODE_AGENTS_COMMANDS_SKILLS_RALPH_AST_GREP_SER}"; shift ;;
    --only) ONLY="${2:-}"; shift 2 ;;
    --target) TARGET="${2:-}"; shift 2 ;;
    --clean) CLEAN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "${TW_MESSAGE_UNKNOWN_OPTION}$1"; usage; exit 2 ;;
  esac
done

if [[ -z "$ONLY" && "$MODE" != "$TW_MODE_CHECK" ]]; then
  echo "${SH_SELECT_COMPONENTS_WITH_ALL_OR_ONLY_REFUSING_TO_GUE}"
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
  if [[ "$MODE" == "$TW_MODE_APPLY" ]]; then
    "$@"
  else
    printf "${SH_WOULD_RUN_S_N}" "$*"
  fi
}

echo "mode=$MODE target=$TARGET"

echo "${SH_DEPENDENCIES}"
for c in git node python3 rg; do
  if has "$c"; then printf "${SH_OK_10S_S_N}" "$c" "$(command -v "$c")"; else printf "${SH_MISS_10S_N}" "$c"; fi
done
printf "${SH_INFO_OPENCODE_S_N}" "$(opencode --version 2>/dev/null || echo 'not installed')"
printf "${SH_INFO_RALPH_S_N}" "$(ralph --version 2>/dev/null || echo 'not installed')"
printf "${SH_INFO_AST_GREP_S_N}" "$(ast-grep --version 2>/dev/null | head -1 || echo 'not installed')"
printf "${SH_INFO_SERENA_S_N}" "$(serena --version 2>/dev/null || echo 'not installed')"
printf "${SH_INFO_CODEGRAPH_S_N}" "$(codegraph --version 2>/dev/null || echo 'not installed')"

if [[ "$MODE" == "$TW_MODE_CHECK" ]]; then
  echo "$TW_MESSAGE_CHECK_COMPLETE"
  exit 0
fi

STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP="$TARGET/.opencode-backup-$STAMP"
if [[ "$MODE" == "$TW_MODE_APPLY" ]]; then
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
  if [[ "$MODE" == "$TW_MODE_APPLY" ]]; then
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
  if [[ -f "$dst" && "$MODE" == "$TW_MODE_APPLY" ]]; then
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
  if [[ -d "$dst" && "$MODE" == "$TW_MODE_APPLY" ]]; then
    mkdir -p "$BACKUP/${dst#"$TARGET"/}"
    cp -R "$dst/." "$BACKUP/${dst#"$TARGET"/}/"
  fi
  run mkdir -p "$dst"
  run cp -R "$src/." "$dst/"
}

if [[ "$CLEAN" == "1" ]]; then
  echo "${SH_CLEAN_MANAGED_DIRECTORIES}"
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
  echo "$TW_LABEL_OPENCODE_PLUGIN"
  run mkdir -p "$TARGET/.opencode/plugins"
  copy_file "$ROOT/configs/opencode/plugins/toolwright-memory.js" "$TARGET/.opencode/plugins/toolwright-memory.js"
fi

if selected ralph; then
    clean_dir "$TARGET/.ralph/hats"
  fi
fi

if selected opencode; then
  echo "${SH_OPENCODE_CONFIG}"
  run mkdir -p "$TARGET/.opencode/agents" "$TARGET/.opencode/commands" "$TARGET/.opencode/skills"
  copy_file "$ROOT/configs/opencode/opencode.jsonc" "$TARGET/.opencode/opencode.jsonc"
fi

if selected agents; then
  echo "${SH_AGENTS}"
  run mkdir -p "$TARGET/.opencode/agents"
  for f in "$ROOT"/agents/*/AGENT.md; do
    role="$(basename "$(dirname "$f")")"
    copy_file "$f" "$TARGET/.opencode/agents/$role.md"
  done
fi

if selected commands; then
  echo "${SH_COMMANDS}"
  run mkdir -p "$TARGET/.opencode/commands"
  for f in "$ROOT"/commands/*.md; do
    copy_file "$f" "$TARGET/.opencode/commands/$(basename "$f")"
  done
fi

if selected skills; then
  echo "${SH_SKILLS}"
  run mkdir -p "$TARGET/.opencode/skills"
  for d in "$ROOT"/skills/*/; do
    name="$(basename "$d")"
    copy_dir "$d" "$TARGET/.opencode/skills/$name"
  done
fi

if selected plugin; then
  echo "$TW_LABEL_OPENCODE_PLUGIN"
  run mkdir -p "$TARGET/.opencode/plugins"
  copy_file "$ROOT/configs/opencode/plugins/toolwright-memory.js" "$TARGET/.opencode/plugins/toolwright-memory.js"
fi

if selected ralph; then
  echo "${SH_RALPH_CONFIGS}"
  run mkdir -p "$TARGET/.ralph"
  copy_file "$ROOT/configs/ralph/ralph.yml" "$TARGET/.ralph/ralph.yml"
  run mkdir -p "$TARGET/.ralph/hats"
  for f in "$ROOT"/configs/ralph/hats/*.yml; do
    copy_file "$f" "$TARGET/.ralph/hats/$(basename "$f")"
  done
fi

if selected ast-grep; then
  echo "${SH_AST_GREP}"
  if has ast-grep; then
    echo "$TW_MESSAGE_ALREADY_INSTALLED"
  elif has brew; then
    run brew install ast-grep
  else
    echo "${SH_INSTALL_MANUALLY_NPM_INSTALL_GLOBAL_AST_GREP_CLI}"
  fi
fi

if selected serena; then
  echo "${SH_SERENA}"
  if has serena; then
    echo "$TW_MESSAGE_ALREADY_INSTALLED"
  elif has uv; then
    run uv tool install -p 3.13 serena-agent
  else
    echo "${SH_INSTALL_UV_FIRST_HTTPS_DOCS_ASTRAL_SH_UV_GETTING_S}"
  fi
fi

if selected codegraph; then
  echo "${SH_CODEGRAPH_LABEL}"
  if has codegraph; then
    echo "$TW_MESSAGE_ALREADY_INSTALLED"
  else
    echo "${SH_INSTALL_MANUALLY}"
    echo "${SH_CURL_FSSL_HTTPS_RAW_GITHUBUSERCONTENT_COM_COLBYMCH}"
    echo "${SH_NOTE_INSTALLER_DOWNLOADS_AND_EXECUTES_A_REMOTE_SCR}"
  fi
fi

if [[ "$MODE" == "$TW_MODE_APPLY" ]]; then
  echo "backup: $BACKUP"
  echo "${SH_VERIFY_OPENCODE_DEBUG_CONFIG_OPENCODE_DEBUG_AGENTS}"
  echo "rollback: copy files back from $BACKUP"
fi
