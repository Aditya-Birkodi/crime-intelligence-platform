#!/usr/bin/env bash
# Local development bootstrap for Crime Intelligence Platform.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

echo "Syncing Python deps with uv..."
if command -v uv >/dev/null 2>&1; then
  uv sync --extra dev
  uv run pre-commit install || true
else
  echo "uv not found — install from https://docs.astral.sh/uv/"
  python3 -m pip install -r requirements.txt
fi

echo "Starting Postgres + Redis (local only; prod uses Catalyst)..."
docker compose up -d

echo "Done. Next:"
echo "  uv run uvicorn backend.main:app --reload --app-dir ."
echo "  cd frontend && npm install && npm run dev"
