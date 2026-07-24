"""Synthetic Karnataka-like masters + FIR seeds (no real PII).

Deprecated entrypoint — use seed_fir_dataset.py (Police_FIR_ER_Diagram.pdf dataset).

Usage (from repo root, Postgres up):
  PYTHONPATH=backend python database/seed/seed_b1.py
  PYTHONPATH=backend python database/seed/seed_b1.py --force
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from seed_fir_dataset import main as seed_main  # noqa: E402

if __name__ == "__main__":
    # Default to postgres for backwards compatibility with older docs/scripts
    if "--target" not in sys.argv:
        sys.argv.extend(["--target", "postgres"])
    seed_main()
