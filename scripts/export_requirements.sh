#!/usr/bin/env bash
# Export / refresh requirements.txt from pyproject.toml via uv.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required for this script"
  exit 1
fi

# Keep a human-readable requirements.txt in sync with declared deps.
uv pip compile pyproject.toml -o requirements.txt --extra dev
echo "Wrote requirements.txt"
