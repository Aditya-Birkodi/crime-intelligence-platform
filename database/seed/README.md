# Seed data

## B1 seed (synthetic FIRs)

```bash
# Postgres must be running (docker compose up -d)
PYTHONPATH=backend uv run python database/seed/seed_b1.py
```

Creates masters + 4 FIRs across Bengaluru City, Mysuru, Belagavi.
No real personal data.

## Alembic

```bash
uv run alembic -c backend/alembic.ini upgrade head
```
