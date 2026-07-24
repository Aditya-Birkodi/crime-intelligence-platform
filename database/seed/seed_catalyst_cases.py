"""Seed sample FIRs into Catalyst Data Store mock (local JSON file).

Delegates to seed_fir_dataset.py (Police_FIR_ER_Diagram.pdf aligned dataset).

Usage:
  PERSISTENCE_BACKEND=catalyst CATALYST_DATASTORE_MOCK=true \\
    PYTHONPATH=backend python database/seed/seed_catalyst_cases.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from seed_fir_dataset import main as seed_main  # noqa: E402

if __name__ == "__main__":
    if "--target" not in sys.argv:
        sys.argv.extend(["--target", "catalyst-mock"])
    seed_main()
