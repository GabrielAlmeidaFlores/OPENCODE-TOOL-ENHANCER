#!/usr/bin/env bash
# Name: Local release check
# Purpose: Reproduces the release workflow locally: version check, wheel build, checksum, and checksum verification.
# Usage: ./scripts/release/local_release_check.sh
# Arguments: None.
# Environment: Requires bash, python3, and pip; uses sha256sum or shasum.
# Outputs: Prints the wheel path and checksum verification result.
# Side effects: Creates a temporary directory and removes it on exit.
# References: docs/release/README.md, .github/workflows/release.yml
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

python3 "$ROOT/scripts/release/check_version.py"
python3 -m pip wheel "$ROOT/packages/ote_cli" --no-deps --wheel-dir "$TMP" --quiet

cd "$TMP"
if command -v sha256sum >/dev/null 2>&1; then
  sha256sum ./*.whl > SHA256SUMS
  sha256sum -c SHA256SUMS
else
  shasum -a 256 ./*.whl > SHA256SUMS
  shasum -a 256 -c SHA256SUMS
fi

echo "local release check passed"
