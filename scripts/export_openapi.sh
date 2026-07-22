#!/usr/bin/env bash
# Export OpenAPI schema for FE / Postman import.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p openapi

export PATH="${HOME}/.local/bin:${PATH}"

if [[ -x .venv/bin/python ]]; then
  PYTHON=.venv/bin/python
else
  PYTHON=python3
fi

PYTHONPATH=backend "$PYTHON" - <<'PY'
from pathlib import Path
import json
import sys

sys.path.insert(0, "backend")
from main import app

path = Path("openapi/openapi.json")
path.write_text(json.dumps(app.openapi(), indent=2), encoding="utf-8")
print(f"Wrote {path}")
PY
