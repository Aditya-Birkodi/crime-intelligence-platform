"""Synthetic Karnataka-like masters + FIR seeds (no real PII).

Usage (from repo root, Postgres up):
  PYTHONPATH=backend uv run python database/seed/seed_b1.py
"""

from __future__ import annotations

import sys
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from sqlalchemy import select

from app.database.base import Base
from app.database.session import SessionLocal, engine
from app.models import (  # noqa: F401 — register metadata
    Accused,
    Act,
    ActSectionAssociation,
    CaseCategory,
    CaseMaster,
    CaseStatusMaster,
    CrimeHead,
    CrimeSubHead,
    District,
    GravityOffence,
    Section,
    State,
    Unit,
    UnitType,
    Victim,
)
from app.utils.crime_no import build_crime_no, parse_crime_no


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        if session.scalar(select(CaseMaster).limit(1)) is not None:
            print("Seed skipped — cases already present")
            return

        # Lookups
        statuses = [
            CaseStatusMaster(case_status_name="Under Investigation"),
            CaseStatusMaster(case_status_name="Charge Sheeted"),
            CaseStatusMaster(case_status_name="Closed"),
        ]
        categories = [
            CaseCategory(lookup_value="FIR", category_code="1"),
            CaseCategory(lookup_value="UDR", category_code="3"),
            CaseCategory(lookup_value="PAR", category_code="4"),
            CaseCategory(lookup_value="Zero FIR", category_code="8"),
        ]
        gravities = [
            GravityOffence(lookup_value="Heinous"),
            GravityOffence(lookup_value="Non-Heinous"),
        ]
        session.add_all(statuses + categories + gravities)
        session.flush()

        state = State(state_name="Karnataka", active=True)
        session.add(state)
        session.flush()

        districts = [
            District(
                district_id=443, district_name="Bengaluru City", state_id=state.state_id
            ),
            District(district_id=444, district_name="Mysuru", state_id=state.state_id),
            District(
                district_id=445, district_name="Belagavi", state_id=state.state_id
            ),
        ]
        session.add_all(districts)

        unit_type = UnitType(
            unit_type_name="Police Station", city_dist_state="City", hierarchy=1
        )
        session.add(unit_type)
        session.flush()

        units = [
            Unit(
                unit_id=6,
                unit_name="MG Road PS",
                type_id=unit_type.unit_type_id,
                state_id=state.state_id,
                district_id=443,
            ),
            Unit(
                unit_id=7,
                unit_name="Indiranagar PS",
                type_id=unit_type.unit_type_id,
                state_id=state.state_id,
                district_id=443,
            ),
            Unit(
                unit_id=11,
                unit_name="Mysuru North PS",
                type_id=unit_type.unit_type_id,
                state_id=state.state_id,
                district_id=444,
            ),
            Unit(
                unit_id=21,
                unit_name="Belagavi Rural PS",
                type_id=unit_type.unit_type_id,
                state_id=state.state_id,
                district_id=445,
            ),
        ]
        session.add_all(units)

        act = Act(act_code="IPC", act_description="Indian Penal Code", short_name="IPC")
        session.add(act)
        session.flush()
        sections = [
            Section(act_code="IPC", section_code="379", section_description="Theft"),
            Section(act_code="IPC", section_code="302", section_description="Murder"),
            Section(act_code="IPC", section_code="420", section_description="Cheating"),
        ]
        session.add_all(sections)

        head_body = CrimeHead(crime_group_name="Crimes Against Body")
        head_property = CrimeHead(crime_group_name="Crimes Against Property")
        session.add_all([head_body, head_property])
        session.flush()
        sub_theft = CrimeSubHead(
            crime_head_id=head_property.crime_head_id,
            crime_head_name="Theft",
            seq_id=1,
        )
        sub_murder = CrimeSubHead(
            crime_head_id=head_body.crime_head_id,
            crime_head_name="Murder",
            seq_id=1,
        )
        session.add_all([sub_theft, sub_murder])
        session.flush()

        fir_cat = next(c for c in categories if c.category_code == "1")
        ui_status = next(
            s for s in statuses if s.case_status_name == "Under Investigation"
        )
        non_heinous = next(g for g in gravities if g.lookup_value == "Non-Heinous")
        heinous = next(g for g in gravities if g.lookup_value == "Heinous")

        samples = [
            {
                "district": 443,
                "station": 6,
                "serial": 1,
                "lat": Decimal("12.9716000"),
                "lon": Decimal("77.5946000"),
                "brief": "Complainant reported theft of a two-wheeler near MG Road. Accused fled on foot.",
                "head": head_property,
                "sub": sub_theft,
                "section": "379",
                "gravity": non_heinous,
                "victim": "Ravi Kumar",
                "accused": "Unknown A1",
            },
            {
                "district": 443,
                "station": 7,
                "serial": 2,
                "lat": Decimal("12.9784000"),
                "lon": Decimal("77.6408000"),
                "brief": "Mobile phone snatched near 100 Feet Road. CCTV footage under review.",
                "head": head_property,
                "sub": sub_theft,
                "section": "379",
                "gravity": non_heinous,
                "victim": "Anita Sharma",
                "accused": "Suresh M",
            },
            {
                "district": 444,
                "station": 11,
                "serial": 1,
                "lat": Decimal("12.2958000"),
                "lon": Decimal("76.6394000"),
                "brief": "Cheating complaint regarding online investment fraud targeting local traders.",
                "head": head_property,
                "sub": sub_theft,
                "section": "420",
                "gravity": non_heinous,
                "victim": "Local Traders Collective",
                "accused": "Fake Broker Ring",
            },
            {
                "district": 445,
                "station": 21,
                "serial": 1,
                "lat": Decimal("15.8497000"),
                "lon": Decimal("74.4977000"),
                "brief": "Homicide investigation following altercation at village fair. Forensic team notified.",
                "head": head_body,
                "sub": sub_murder,
                "section": "302",
                "gravity": heinous,
                "victim": "Village Resident",
                "accused": "Suspect A1",
            },
        ]

        for sample in samples:
            crime_no = build_crime_no(
                category_code="1",
                district_id=sample["district"],
                police_station_id=sample["station"],
                year=2026,
                serial=sample["serial"],
            )
            parsed = parse_crime_no(crime_no)
            case = CaseMaster(
                crime_no=crime_no,
                case_no=parsed.case_no_suffix,
                crime_registered_date=date(2026, 1, 15),
                police_station_id=sample["station"],
                case_category_id=fir_cat.case_category_id,
                gravity_offence_id=sample["gravity"].gravity_offence_id,
                crime_major_head_id=sample["head"].crime_head_id,
                crime_minor_head_id=sample["sub"].crime_sub_head_id,
                case_status_id=ui_status.case_status_id,
                incident_from_date=datetime(2026, 1, 15, 21, 0, tzinfo=UTC),
                incident_to_date=datetime(2026, 1, 15, 23, 0, tzinfo=UTC),
                latitude=sample["lat"],
                longitude=sample["lon"],
                brief_facts=sample["brief"],
                victims=[
                    Victim(victim_name=sample["victim"], age_year=32, gender_id="M")
                ],
                accused=[
                    Accused(
                        accused_name=sample["accused"],
                        age_year=28,
                        gender_id="M",
                        person_id="A1",
                    )
                ],
                act_sections=[
                    ActSectionAssociation(act_id="IPC", section_id=sample["section"])
                ],
            )
            session.add(case)

        session.commit()
        print(f"Seeded {len(samples)} synthetic FIRs across 3 districts")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed()
