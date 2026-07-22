"""Seed sample FIRs into Catalyst Data Store mock (local JSON file).

Usage:
  PERSISTENCE_BACKEND=catalyst CATALYST_DATASTORE_MOCK=true \\
    PYTHONPATH=backend uv run python database/seed/seed_catalyst_cases.py
"""

from __future__ import annotations

import os
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

# Force mock catalyst before settings cache
os.environ.setdefault("PERSISTENCE_BACKEND", "catalyst")
os.environ.setdefault("CATALYST_DATASTORE_MOCK", "true")

from app.core.config import get_settings
from app.repositories.case.catalyst_case_store import CatalystCaseStore
from app.schemas.case.case_master import (
    AccusedCreate,
    ActSectionCreate,
    CaseMasterCreate,
    VictimCreate,
)


def main() -> None:
    get_settings.cache_clear()
    store = CatalystCaseStore()
    samples = [
        CaseMasterCreate(
            crime_no="104430006202600001",
            case_no="202600001",
            crime_registered_date=date(2026, 1, 15),
            police_station_id=6,
            case_category_id=1,
            case_status_id=1,
            crime_major_head_id=1,
            latitude=Decimal("12.971600"),
            longitude=Decimal("77.594600"),
            brief_facts="Theft near MG Road (Catalyst seed)",
            victims=[VictimCreate(victim_name="Ravi Kumar", gender_id="M")],
            accused=[AccusedCreate(accused_name="Unknown", person_id="U1")],
            act_sections=[ActSectionCreate(act_id="IPC", section_id="379")],
        ),
        CaseMasterCreate(
            crime_no="104430006202600002",
            case_no="202600002",
            crime_registered_date=date(2026, 2, 3),
            police_station_id=6,
            case_category_id=1,
            case_status_id=1,
            brief_facts="Assault complaint (Catalyst seed)",
            victims=[VictimCreate(victim_name="Anita S", gender_id="F")],
            accused=[AccusedCreate(accused_name="Suresh P", person_id="A2")],
            act_sections=[ActSectionCreate(act_id="IPC", section_id="323")],
        ),
    ]
    created = 0
    for payload in samples:
        if store.get_by_crime_no(payload.crime_no) is not None:
            print(f"skip existing {payload.crime_no}")
            continue
        detail = store.create(payload, case_no=payload.case_no)
        print(
            f"created case_master_id={detail.case_master_id} crime_no={detail.crime_no}"
        )
        created += 1
    print(
        f"done created={created} mock_path={get_settings().catalyst.datastore_mock_path}"
    )


if __name__ == "__main__":
    main()
