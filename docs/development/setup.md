# Development Setup

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Node.js 20+
- Docker Compose

## Steps

```bash
cp .env.example .env
./scripts/setup_dev.sh
uv run uvicorn backend.main:app --reload --app-dir .
cd frontend && npm install && npm run dev
```

## Tooling

```bash
uv run black backend etl tests
uv run isort backend etl tests
uv run ruff check backend etl tests
uv run mypy backend/app etl
uv run pytest
```

Catalyst CLI / project linking: **TODO** after Catalyst account provisioning.
