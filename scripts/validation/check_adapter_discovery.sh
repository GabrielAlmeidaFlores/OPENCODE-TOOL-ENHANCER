#!/usr/bin/env bash
# Name: Adapter discovery check
# Purpose: Installs the Copilot and Codex adapters into temporary targets, then checks native CLI discovery when each CLI is installed.
# Usage: ./scripts/validation/check_adapter_discovery.sh
# Arguments: none.
# Environment: Requires bash and python3. Uses copilot, codex, and claude only when present.
# Outputs: Prints one result per adapter and exits non-zero when an installed CLI fails discovery.
# Side effects: Creates a temporary directory, writes adapter files there, and removes it on exit. Makes no model calls.
# References: docs/installation/adapter-validation.md, docs/compatibility/README.md
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$ROOT/scripts/lib/strings.sh"
cd "$ROOT"
TMP="$(mktemp -d "${TMPDIR:-/tmp}/${SH_ADAPTER_DISCOVERY_TEMP_PREFIX}.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT
failed=0

# Function: install_adapter
# Description: Installs one adapter profile into a temporary target.
# Arguments: $1 platform name; $2 target directory.
# Returns: Zero on success.
# Side effects: Writes generated adapter files under the target.
install_adapter() {
  PYTHONPATH="$ROOT/packages/toolwright_cli" \
    python3 -m toolwright_cli install \
    --platform "$1" \
    --profile "$SH_ADAPTER_PROFILE" \
    --target "$2" \
    --apply >/dev/null
}

# Function: count_matches
# Description: Counts files under a directory that match a find name pattern.
# Arguments: $1 directory; $2 file name pattern.
# Returns: Prints the match count.
# Side effects: Reads the directory only.
count_matches() {
  find "$1" -name "$2" | wc -l | tr -d ' '
}

# Function: count_skill_directories
# Description: Counts immediate subdirectories under a skills directory.
# Arguments: $1 skills directory.
# Returns: Prints the directory count.
# Side effects: Reads the directory only.
count_skill_directories() {
  find "$1" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' '
}

echo "$SH_ADAPTER_DISCOVERY"

if command -v copilot >/dev/null 2>&1; then
  install_adapter "$SH_ADAPTER_COPILOT" "$TMP/$SH_ADAPTER_COPILOT"
  instructions_actual="$(
    cd "$TMP/$SH_ADAPTER_COPILOT"
    copilot instruction list | grep -c "$SH_COPILOT_INSTRUCTION_SOURCE" || true
  )"
  instructions_expected="$(count_matches "$TMP/$SH_ADAPTER_COPILOT/.github/instructions" "$SH_COPILOT_INSTRUCTIONS_GLOB")"
  skills_actual="$(
    cd "$TMP/$SH_ADAPTER_COPILOT"
    copilot skill list \
      | sed -n "/$SH_COPILOT_SKILLS_SECTION_START/,/$SH_COPILOT_SKILLS_SECTION_END/p" \
      | grep -c "$SH_COPILOT_SKILL_PREFIX" || true
  )"
  skills_expected="$(count_skill_directories "$TMP/$SH_ADAPTER_COPILOT/.github/skills")"
  if [[ "$instructions_actual" -eq "$instructions_expected" ]] \
    && [[ "$skills_actual" -eq "$skills_expected" ]]; then
    echo "$SH_ADAPTER_COPILOT: $SH_ADAPTER_DISCOVERY_OK"
    echo "$SH_ADAPTER_DISCOVERY_COUNT $instructions_actual/$instructions_expected $SH_ADAPTER_DISCOVERY_INSTRUCTIONS"
    echo "$SH_ADAPTER_DISCOVERY_COUNT $skills_actual/$skills_expected $SH_ADAPTER_DISCOVERY_SKILLS"
  else
    echo "$SH_ADAPTER_COPILOT: $SH_ADAPTER_DISCOVERY_FAIL"
    echo "$SH_ADAPTER_DISCOVERY_COUNT $instructions_actual/$instructions_expected $SH_ADAPTER_DISCOVERY_INSTRUCTIONS"
    echo "$SH_ADAPTER_DISCOVERY_COUNT $skills_actual/$skills_expected $SH_ADAPTER_DISCOVERY_SKILLS"
    failed=1
  fi
else
  echo "$SH_ADAPTER_COPILOT: $SH_ADAPTER_DISCOVERY_SKIP"
fi

if command -v codex >/dev/null 2>&1; then
  install_adapter "$SH_ADAPTER_CODEX" "$TMP/$SH_ADAPTER_CODEX"
  if (
    cd "$TMP/$SH_ADAPTER_CODEX"
    codex debug prompt-input "$SH_CODEX_DISCOVERY_PROMPT"
  ) | grep -q "$SH_CODEX_AGENTS_MARKER"; then
    echo "$SH_ADAPTER_CODEX: $SH_ADAPTER_DISCOVERY_OK"
  else
    echo "$SH_ADAPTER_CODEX: $SH_ADAPTER_DISCOVERY_FAIL"
    failed=1
  fi
else
  echo "$SH_ADAPTER_CODEX: $SH_ADAPTER_DISCOVERY_SKIP"
fi

if command -v claude >/dev/null 2>&1; then
  echo "$SH_ADAPTER_CLAUDE: $SH_ADAPTER_DISCOVERY_CLAUDE_SKIP"
else
  echo "$SH_ADAPTER_CLAUDE: $SH_ADAPTER_DISCOVERY_SKIP"
fi

exit "$failed"
