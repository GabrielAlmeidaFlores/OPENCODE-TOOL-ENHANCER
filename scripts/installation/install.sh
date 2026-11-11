#!/usr/bin/env bash
# Selective installer. Defaults to check-only. Never edits ~/.config/opencode.
#
# Usage:
#   ./scripts/installation/install.sh --check
#   ./scripts/installation/install.sh --dry-run --all
#   ./scripts/installation/install.sh --apply --only opencode
#   ./scripts/installation/install.sh --apply --only ast-grep,serena,codegraph
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MODE="check"
ONLY=""
TARGET="$ROOT"
CLEAN=0

usage() {
  cat <<'EOF'
Options:
  --check              Print status only (default)
  --dry-run            Print planned actions without executing
  --apply              Execute selected actions
  --all                Select all components
  --only LIST          Comma-separated: opencode,agents,commands,skills,ralph,ast-grep,serena,codegraph
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

has() { command -v "$1" >/dev/null 2>&1; }
selected() { [[ ",$ONLY," == *",$1,"* ]]; }
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
mkdir -p "$BACKUP"

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

copy_file() {
  local src="$1" dst="$2"
  if [[ -f "$dst" && "$MODE" == "apply" ]]; then
    mkdir -p "$(dirname "$BACKUP/${dst#$TARGET/}")"
    cp "$dst" "$BACKUP/${dst#$TARGET/}"
  fi
  run cp "$src" "$dst"
}

if [[ "$CLEAN" == "1" ]]; then
  echo "== clean managed directories =="
  clean_dir "$TARGET/.opencode/agents"
  clean_dir "$TARGET/.opencode/commands"
  clean_dir "$TARGET/.opencode/skills"
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
    run mkdir -p "$TARGET/.opencode/skills/$name"
    copy_file "${d}SKILL.md" "$TARGET/.opencode/skills/$name/SKILL.md"
  done
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
