"""Seed FIR demo dataset from fir_demo_dataset.yaml (Police_FIR_ER_Diagram.pdf).

Covers analytics + intelligence entities: CaseMaster parties, Inv_OccuranceTime,
ArrestSurrender, ChargesheetDetails, Court, Employee/Rank/Designation,
CrimeHeadActSection, Unit hierarchy.

Usage (from repo root):
  PYTHONPATH=backend python database/seed/seed_fir_dataset.py --force
  PYTHONPATH=backend python database/seed/seed_fir_dataset.py --target catalyst-mock
  PYTHONPATH=backend python database/seed/seed_fir_dataset.py --target postgres --force
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
DATASET_PATH = Path(__file__).resolve().parent / "fir_demo_dataset.yaml"
FULL_DATASET_PATH = Path(__file__).resolve().parent / "fir_full_dataset.yaml"
APPSAIL_MOCK_PATH = Path(__file__).resolve().parent / "appsail_datastore.json"
RAG_DOCS_PATH = Path(__file__).resolve().parent / "fir_rag_documents.json"
AI_FEATURES_PATH = Path(__file__).resolve().parent / "ai_case_features.json"
LOOKUPS_PATH = Path(__file__).resolve().parent / "appsail_lookups.json"
LOCAL_MOCK_PATH = ROOT / ".data" / "catalyst_datastore.json"

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.utils.crime_no import build_crime_no, parse_crime_no  # noqa: E402


def load_dataset(path: Path = DATASET_PATH) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Invalid dataset: {path}")
    return raw


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(str(value)[:10])


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    text = str(value).replace("Z", "+00:00")
    return datetime.fromisoformat(text)


def enrich_cases(data: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for case in data.get("cases") or []:
        crime_no = build_crime_no(
            category_code=str(case["category_code"]),
            district_id=int(case["district_id"]),
            police_station_id=int(case["police_station_id"]),
            year=int(case["year"]),
            serial=int(case["serial"]),
        )
        parsed = parse_crime_no(crime_no)
        enriched = dict(case)
        enriched["crime_no"] = crime_no
        enriched["case_no"] = parsed.case_no_suffix
        out.append(enriched)
    return out


def _id_maps(data: dict[str, Any]) -> dict[str, Any]:
    status_keys = {
        s["key"]: i + 1 for i, s in enumerate(data["masters"]["case_statuses"])
    }
    cat_by_code = {
        str(c["category_code"]): i + 1
        for i, c in enumerate(data["masters"]["case_categories"])
    }
    gravity_keys = {
        g["key"]: i + 1 for i, g in enumerate(data["masters"]["gravity_offences"])
    }
    head_keys: dict[str, int] = {}
    sub_keys: dict[str, int] = {}
    head_id = 1
    sub_id = 1
    for head in data["legal"]["crime_heads"]:
        head_keys[head["key"]] = head_id
        for sub in head.get("sub_heads") or []:
            sub_keys[sub["key"]] = sub_id
            sub_id += 1
        head_id += 1
    court_keys = {
        c["key"]: i + 1
        for i, c in enumerate(data.get("geography", {}).get("courts") or [])
    }
    emp_keys = {
        e["key"]: i + 1
        for i, e in enumerate((data.get("personnel") or {}).get("employees") or [])
    }
    return {
        "status": status_keys,
        "cat": cat_by_code,
        "gravity": gravity_keys,
        "head": head_keys,
        "sub": sub_keys,
        "court": court_keys,
        "emp": emp_keys,
    }


# ---------------------------------------------------------------------------
# Catalyst mock + RAG export
# ---------------------------------------------------------------------------


def export_catalyst_mock(
    data: dict[str, Any],
    *,
    dest: Path = APPSAIL_MOCK_PATH,
    also_local: bool = True,
) -> Path:
    """Write CaseStore + intel tables. ROWIDs are per-table (start at 1)."""
    cases = enrich_cases(data)
    ids = _id_maps(data)
    tables: dict[str, list[dict[str, Any]]] = {
        k: []
        for k in (
            "cip_case_master",
            "cip_victim",
            "cip_accused",
            "cip_act_section_association",
            "cip_complainant_details",
            "cip_inv_occurance_time",
            "cip_arrest_surrender",
            "cip_inv_arrest_surrender_accused",
            "cip_chargesheet_details",
            "cip_court",
            "cip_employee",
            "cip_rank",
            "cip_designation",
            "cip_crime_head_act_section",
        )
    }
    counters: dict[str, int] = {k: 1 for k in tables}

    def _row(table: str, payload: dict[str, Any]) -> dict[str, Any]:
        rid = counters[table]
        counters[table] = rid + 1
        stored = {"ROWID": rid, **payload}
        tables[table].append(stored)
        return stored

    for i, r in enumerate((data.get("personnel") or {}).get("ranks") or [], start=1):
        tables["cip_rank"].append(
            {
                "ROWID": i,
                "rank_id": i,
                "rank_name": r["name"],
                "hierarchy": r.get("hierarchy", 1),
            }
        )
        counters["cip_rank"] = i + 1
    for i, d in enumerate(
        (data.get("personnel") or {}).get("designations") or [], start=1
    ):
        tables["cip_designation"].append(
            {
                "ROWID": i,
                "designation_id": i,
                "designation_name": d["name"],
                "sort_order": d.get("sort_order", 0),
            }
        )
        counters["cip_designation"] = i + 1

    rank_key = {
        r["key"]: i + 1
        for i, r in enumerate((data.get("personnel") or {}).get("ranks") or [])
    }
    des_key = {
        d["key"]: i + 1
        for i, d in enumerate((data.get("personnel") or {}).get("designations") or [])
    }
    for e in (data.get("personnel") or {}).get("employees") or []:
        eid = ids["emp"][e["key"]]
        tables["cip_employee"].append(
            {
                "ROWID": eid,
                "employee_id": eid,
                "district_id": e["district_id"],
                "unit_id": e["unit_id"],
                "rank_id": rank_key[e["rank"]],
                "designation_id": des_key[e["designation"]],
                "kgid": e["kgid"],
                "first_name": e["first_name"],
                "gender_id": e.get("gender_id"),
                "appointment_date": e.get("appointment_date"),
            }
        )
        counters["cip_employee"] = max(counters["cip_employee"], eid + 1)

    for c in data.get("geography", {}).get("courts") or []:
        cid = ids["court"][c["key"]]
        tables["cip_court"].append(
            {
                "ROWID": cid,
                "court_id": cid,
                "court_name": c["name"],
                "district_id": c["district_id"],
                "state_id": 1,
                "active": True,
            }
        )
        counters["cip_court"] = max(counters["cip_court"], cid + 1)

    for m in data.get("legal", {}).get("crime_head_act_sections") or []:
        _row(
            "cip_crime_head_act_section",
            {
                "crime_head_id": ids["head"].get(m["major_head"]),
                "act_code": m["act_code"],
                "section_code": str(m["section_code"]),
            },
        )

    accused_by_case_person: dict[tuple[int, str], int] = {}

    for case in cases:
        officer_key = case.get("registering_officer")
        court_key = case.get("court")
        case_row = _row(
            "cip_case_master",
            {
                "crime_no": case["crime_no"],
                "case_no": case["case_no"],
                "crime_registered_date": case.get("registered_date"),
                "police_person_id": (
                    ids["emp"].get(officer_key) if officer_key else None
                ),
                "police_station_id": int(case["police_station_id"]),
                "case_category_id": ids["cat"][str(case["category_code"])],
                "gravity_offence_id": ids["gravity"].get(case.get("gravity") or ""),
                "crime_major_head_id": ids["head"].get(case.get("major_head") or ""),
                "crime_minor_head_id": ids["sub"].get(case.get("minor_head") or ""),
                "case_status_id": ids["status"][case["status"]],
                "court_id": ids["court"].get(court_key) if court_key else None,
                "incident_from_date": case.get("incident_from"),
                "incident_to_date": case.get("incident_to"),
                "info_received_ps_date": case.get("info_received"),
                "latitude": case.get("latitude"),
                "longitude": case.get("longitude"),
                "brief_facts": case.get("brief_facts"),
            },
        )
        case_id = int(case_row["ROWID"])

        for v in case.get("victims") or []:
            _row(
                "cip_victim",
                {
                    "case_master_id": case_id,
                    "victim_name": v["name"],
                    "age_year": v.get("age_year"),
                    "gender_id": v.get("gender_id"),
                    "victim_police": v.get("victim_police", "0"),
                },
            )
        for a in case.get("accused") or []:
            arow = _row(
                "cip_accused",
                {
                    "case_master_id": case_id,
                    "accused_name": a["name"],
                    "age_year": a.get("age_year"),
                    "gender_id": a.get("gender_id"),
                    "person_id": a.get("person_id"),
                },
            )
            if a.get("person_id"):
                accused_by_case_person[(case_id, str(a["person_id"]))] = int(
                    arow["ROWID"]
                )
        for s in case.get("act_sections") or []:
            _row(
                "cip_act_section_association",
                {
                    "case_master_id": case_id,
                    "act_id": s["act_id"],
                    "section_id": str(s["section_id"]),
                    "act_order_id": int(s.get("act_order_id") or 1),
                    "section_order_id": int(s.get("section_order_id") or 1),
                },
            )
        for c in case.get("complainants") or []:
            _row(
                "cip_complainant_details",
                {
                    "case_master_id": case_id,
                    "complainant_name": c["name"],
                    "age_year": c.get("age_year"),
                    "gender_id": c.get("gender_id"),
                    "occupation_key": c.get("occupation"),
                    "religion_key": c.get("religion"),
                    "caste_key": c.get("caste"),
                },
            )

        occ = case.get("occurrence") or {}
        if occ:
            tables["cip_inv_occurance_time"].append(
                {
                    "ROWID": case_id,
                    "case_master_id": case_id,
                    "occurrence_from": occ.get("occurrence_from"),
                    "occurrence_to": occ.get("occurrence_to"),
                    "place_of_occurrence": occ.get("place_of_occurrence"),
                    "beat_number": occ.get("beat_number"),
                    "distance_from_ps_km": occ.get("distance_from_ps_km"),
                    "direction_from_ps": occ.get("direction_from_ps"),
                    "village_or_city": occ.get("village_or_city"),
                }
            )

        for ar in case.get("arrests") or []:
            aid = accused_by_case_person.get(
                (case_id, str(ar.get("accused_person_id") or ""))
            )
            arrest_row = _row(
                "cip_arrest_surrender",
                {
                    "case_master_id": case_id,
                    "arrest_surrender_type_id": int(ar.get("type_id") or 1),
                    "arrest_surrender_date": ar.get("date"),
                    "arrest_surrender_state_id": 1,
                    "arrest_surrender_district_id": int(case["district_id"]),
                    "police_station_id": int(case["police_station_id"]),
                    "io_id": ids["emp"].get(ar.get("io") or ""),
                    "court_id": ids["court"].get(ar.get("court") or ""),
                    "accused_master_id": aid,
                    "is_accused": bool(ar.get("is_accused", True)),
                    "is_complainant_accused": False,
                },
            )
            if aid:
                _row(
                    "cip_inv_arrest_surrender_accused",
                    {
                        "arrest_surrender_id": int(arrest_row["ROWID"]),
                        "accused_master_id": aid,
                    },
                )

        cs = case.get("chargesheet")
        if cs:
            _row(
                "cip_chargesheet_details",
                {
                    "case_master_id": case_id,
                    "cs_date": cs.get("cs_date"),
                    "cs_type": cs.get("cs_type", "A"),
                    "police_person_id": ids["emp"].get(cs.get("police_person") or ""),
                },
            )

    payload = {"seq": max(counters.values()), "tables": tables}
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    if also_local:
        LOCAL_MOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(dest, LOCAL_MOCK_PATH)
    print(
        f"catalyst-mock: {len(tables['cip_case_master'])} cases, "
        f"{len(tables['cip_arrest_surrender'])} arrests, "
        f"{len(tables['cip_chargesheet_details'])} chargesheets → {dest}"
    )
    return dest


def export_rag_documents(data: dict[str, Any], *, dest: Path = RAG_DOCS_PATH) -> Path:
    """Build QuickML/NoSQL-ready RAG docs for intelligence (B4)."""
    cases = enrich_cases(data)
    docs: list[dict[str, Any]] = []
    now = datetime.now(tz=UTC).isoformat()
    for idx, case in enumerate(cases, start=1):
        sections = case.get("act_sections") or []
        section_parts = [f"{s.get('act_id')} {s.get('section_id')}" for s in sections]
        occ = case.get("occurrence") or {}
        accused_names = ", ".join(a["name"] for a in (case.get("accused") or []))
        victim_names = ", ".join(v["name"] for v in (case.get("victims") or []))
        text = (
            f"CrimeNo: {case['crime_no']}\n"
            f"Brief Facts: {case.get('brief_facts') or ''}\n"
            f"Sections: {'; '.join(section_parts)}\n"
            f"Place: {occ.get('place_of_occurrence') or ''}\n"
            f"Victims: {victim_names}\n"
            f"Accused: {accused_names}\n"
        )
        docs.append(
            {
                "doc_id": f"case:{case['crime_no']}",
                "case_master_id": idx,
                "crime_no": case["crime_no"],
                "case_no": case["case_no"],
                "police_station_id": case["police_station_id"],
                "district_id": case["district_id"],
                "case_status": case.get("status"),
                "crime_major_head": case.get("major_head"),
                "brief_facts": case.get("brief_facts"),
                "act_sections": [
                    {
                        "act_code": s.get("act_id"),
                        "section_code": str(s.get("section_id")),
                    }
                    for s in sections
                ],
                "incident_from": case.get("incident_from"),
                "incident_to": case.get("incident_to"),
                "latitude": case.get("latitude"),
                "longitude": case.get("longitude"),
                "place_of_occurrence": occ.get("place_of_occurrence"),
                "text_blob": text,
                "source": "fir_demo_dataset",
                "indexed_at": now,
            }
        )
    dest.write_text(json.dumps(docs, indent=2) + "\n", encoding="utf-8")
    print(f"rag-docs: {len(docs)} documents → {dest}")
    return dest


def export_ai_features(data: dict[str, Any], *, dest: Path = AI_FEATURES_PATH) -> Path:
    """Persist per-case risk features for B4 predict/anomaly (from import + heuristics)."""
    cases = enrich_cases(data)
    features: list[dict[str, Any]] = []
    for idx, case in enumerate(cases, start=1):
        brief = str(case.get("brief_facts") or "")
        risk = 50
        severity = "Medium"
        if "Severity: High" in brief:
            severity = "High"
            risk = 75
        elif "Severity: Low" in brief:
            severity = "Low"
            risk = 30
        # pull numeric risk if present in brief from KSP import
        m = re.search(r"RiskScore:\s*(\d+)", brief, flags=re.I)
        if m:
            risk = int(m.group(1))
            severity = (
                "High"
                if "Severity: High" in brief
                else "Low" if "Severity: Low" in brief else "Medium"
            )
        # KSP importer embeds "Severity: X" — also check source risk via arrests
        accused_n = len(case.get("accused") or [])
        arrest_n = len(case.get("arrests") or [])
        if case.get("chargesheet"):
            risk = min(100, risk + 5)
        risk = min(100, risk + accused_n * 2 + arrest_n * 3)
        features.append(
            {
                "case_master_id": idx,
                "crime_no": case["crime_no"],
                "district_id": case["district_id"],
                "police_station_id": case["police_station_id"],
                "crime_major_head": case.get("major_head"),
                "case_status": case.get("status"),
                "severity": severity,
                "risk_score": risk,
                "accused_count": accused_n,
                "arrest_count": arrest_n,
                "has_chargesheet": bool(case.get("chargesheet")),
                "latitude": case.get("latitude"),
                "longitude": case.get("longitude"),
            }
        )
    dest.write_text(json.dumps(features, indent=2) + "\n", encoding="utf-8")
    print(f"ai-features: {len(features)} rows → {dest}")
    return dest


def export_lookups(data: dict[str, Any], *, dest: Path = LOOKUPS_PATH) -> Path:
    """Static lookup snapshot for AppSail (no Postgres). IDs match catalyst mock maps."""
    ids = _id_maps(data)
    geo = data.get("geography") or {}
    masters = data.get("masters") or {}
    personnel = data.get("personnel") or {}

    stations = []
    station_district: dict[str, int] = {}
    for u in geo.get("units") or []:
        uid = int(u["id"])
        did = int(u["district_id"])
        station_district[str(uid)] = did
        if (u.get("type_key") or "ps") == "ps":
            stations.append({"id": uid, "name": u["name"], "district_id": did})

    courts = []
    for i, c in enumerate(geo.get("courts") or [], start=1):
        courts.append(
            {
                "id": i,
                "name": c["name"],
                "district_id": int(c["district_id"]),
                "key": c.get("key"),
            }
        )

    employees = []
    for i, e in enumerate(personnel.get("employees") or [], start=1):
        employees.append(
            {
                "id": i,
                "name": e.get("first_name") or e.get("key") or f"Employee {i}",
                "key": e.get("key"),
                "unit_id": e.get("unit_id"),
                "district_id": e.get("district_id"),
            }
        )

    heads = []
    for key, hid in sorted(ids["head"].items(), key=lambda kv: kv[1]):
        name = next(
            (
                h["group_name"]
                for h in (data.get("legal") or {}).get("crime_heads") or []
                if h.get("key") == key
            ),
            key,
        )
        heads.append({"id": hid, "name": name, "key": key})

    payload = {
        "case_statuses": [
            {"id": i + 1, "name": s["name"], "key": s["key"]}
            for i, s in enumerate(masters.get("case_statuses") or [])
        ],
        "case_categories": [
            {
                "id": i + 1,
                "name": c["lookup_value"],
                "key": c.get("key"),
                "category_code": str(c.get("category_code")),
            }
            for i, c in enumerate(masters.get("case_categories") or [])
        ],
        "gravity_offences": [
            {"id": i + 1, "name": g["lookup_value"], "key": g["key"]}
            for i, g in enumerate(masters.get("gravity_offences") or [])
        ],
        "crime_heads": heads,
        "districts": [
            {"id": int(d["id"]), "name": d["name"]} for d in geo.get("districts") or []
        ],
        "stations": stations,
        "courts": courts,
        "employees": employees,
        "station_district": station_district,
    }
    dest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        f"lookups: {len(stations)} stations, {len(payload['districts'])} districts → {dest}"
    )
    return dest


# ---------------------------------------------------------------------------
# Postgres seed
# ---------------------------------------------------------------------------


def seed_postgres(data: dict[str, Any], *, force: bool = False) -> None:
    from sqlalchemy import select

    from app.database.base import Base
    from app.database.session import SessionLocal, engine
    from app.models import (
        Accused,
        Act,
        ActSectionAssociation,
        ArrestSurrender,
        CaseCategory,
        CaseMaster,
        CaseStatusMaster,
        CasteMaster,
        ChargesheetDetails,
        ComplainantDetails,
        Court,
        CrimeHead,
        CrimeHeadActSection,
        CrimeSubHead,
        Designation,
        District,
        Employee,
        GravityOffence,
        InvArrestSurrenderAccused,
        InvOccuranceTime,
        OccupationMaster,
        Rank,
        ReligionMaster,
        Section,
        State,
        Unit,
        UnitType,
        Victim,
    )

    if force:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        existing = session.scalar(select(CaseMaster).limit(1))
        if existing is not None and not force:
            print("postgres: skipped — cases already present (use --force)")
            return

        masters = data["masters"]
        status_map: dict[str, CaseStatusMaster] = {}
        for item in masters["case_statuses"]:
            row = CaseStatusMaster(case_status_name=item["name"])
            session.add(row)
            session.flush()
            status_map[item["key"]] = row

        category_by_code: dict[str, CaseCategory] = {}
        for item in masters["case_categories"]:
            row = CaseCategory(
                lookup_value=item["lookup_value"],
                category_code=str(item["category_code"]),
            )
            session.add(row)
            session.flush()
            category_by_code[str(item["category_code"])] = row

        gravity_map: dict[str, GravityOffence] = {}
        for item in masters["gravity_offences"]:
            row = GravityOffence(lookup_value=item["lookup_value"])
            session.add(row)
            session.flush()
            gravity_map[item["key"]] = row

        occ_map: dict[str, OccupationMaster] = {}
        for item in masters["occupations"]:
            row = OccupationMaster(occupation_name=item["name"])
            session.add(row)
            session.flush()
            occ_map[item["key"]] = row

        rel_map: dict[str, ReligionMaster] = {}
        for item in masters["religions"]:
            row = ReligionMaster(religion_name=item["name"])
            session.add(row)
            session.flush()
            rel_map[item["key"]] = row

        caste_map: dict[str, CasteMaster] = {}
        for item in masters["castes"]:
            row = CasteMaster(caste_master_name=item["name"])
            session.add(row)
            session.flush()
            caste_map[item["key"]] = row

        geo = data["geography"]
        state = State(
            state_name=geo["state"]["name"],
            active=bool(geo["state"].get("active", True)),
        )
        session.add(state)
        session.flush()

        for d in geo["districts"]:
            session.add(
                District(
                    district_id=int(d["id"]),
                    district_name=d["name"],
                    state_id=state.state_id,
                )
            )

        type_map: dict[str, UnitType] = {}
        unit_types = geo.get("unit_types") or [{**geo["unit_type"], "key": "ps"}]
        for ut in unit_types:
            row = UnitType(
                unit_type_name=ut["name"],
                city_dist_state=ut.get("city_dist_state"),
                hierarchy=int(ut.get("hierarchy") or 1),
            )
            session.add(row)
            session.flush()
            type_map[ut.get("key") or ut["name"]] = row

        # Units: parents first (circles), then stations
        unit_rows = sorted(
            geo["units"],
            key=lambda u: 0 if (u.get("type_key") == "circle") else 1,
        )
        for u in unit_rows:
            type_key = u.get("type_key") or "ps"
            session.add(
                Unit(
                    unit_id=int(u["id"]),
                    unit_name=u["name"],
                    type_id=type_map[type_key].unit_type_id,
                    parent_unit=u.get("parent_unit"),
                    state_id=state.state_id,
                    district_id=int(u["district_id"]),
                )
            )
        session.flush()

        court_map: dict[str, Court] = {}
        for c in geo.get("courts") or []:
            row = Court(
                court_name=c["name"],
                district_id=int(c["district_id"]),
                state_id=state.state_id,
            )
            session.add(row)
            session.flush()
            court_map[c["key"]] = row

        for act in data["legal"]["acts"]:
            session.add(
                Act(
                    act_code=act["code"],
                    act_description=act["description"],
                    short_name=act.get("short_name"),
                )
            )
        session.flush()
        for sec in data["legal"]["sections"]:
            session.add(
                Section(
                    act_code=sec["act_code"],
                    section_code=str(sec["code"]),
                    section_description=sec["description"],
                )
            )

        head_map: dict[str, CrimeHead] = {}
        sub_map: dict[str, CrimeSubHead] = {}
        for head in data["legal"]["crime_heads"]:
            ch = CrimeHead(crime_group_name=head["group_name"])
            session.add(ch)
            session.flush()
            head_map[head["key"]] = ch
            for sub in head.get("sub_heads") or []:
                sh = CrimeSubHead(
                    crime_head_id=ch.crime_head_id,
                    crime_head_name=sub["name"],
                    seq_id=int(sub.get("seq_id") or 1),
                )
                session.add(sh)
                session.flush()
                sub_map[sub["key"]] = sh

        for m in data["legal"].get("crime_head_act_sections") or []:
            session.add(
                CrimeHeadActSection(
                    crime_head_id=head_map[m["major_head"]].crime_head_id,
                    act_code=m["act_code"],
                    section_code=str(m["section_code"]),
                )
            )

        personnel = data.get("personnel") or {}
        rank_map: dict[str, Rank] = {}
        for r in personnel.get("ranks") or []:
            row = Rank(rank_name=r["name"], hierarchy=int(r.get("hierarchy") or 1))
            session.add(row)
            session.flush()
            rank_map[r["key"]] = row
        des_map: dict[str, Designation] = {}
        for d in personnel.get("designations") or []:
            row = Designation(
                designation_name=d["name"],
                sort_order=int(d.get("sort_order") or 0),
            )
            session.add(row)
            session.flush()
            des_map[d["key"]] = row
        emp_map: dict[str, Employee] = {}
        for e in personnel.get("employees") or []:
            row = Employee(
                district_id=int(e["district_id"]),
                unit_id=int(e["unit_id"]),
                rank_id=rank_map[e["rank"]].rank_id,
                designation_id=des_map[e["designation"]].designation_id,
                kgid=e["kgid"],
                first_name=e["first_name"],
                gender_id=e.get("gender_id"),
                appointment_date=_parse_date(e.get("appointment_date")),
            )
            session.add(row)
            session.flush()
            emp_map[e["key"]] = row

        session.flush()
        cases = enrich_cases(data)
        for case in cases:
            major = head_map.get(case.get("major_head") or "")
            minor = sub_map.get(case.get("minor_head") or "")
            gravity = gravity_map.get(case.get("gravity") or "")
            officer = emp_map.get(case.get("registering_officer") or "")
            court = court_map.get(case.get("court") or "")
            entity = CaseMaster(
                crime_no=case["crime_no"],
                case_no=case["case_no"],
                crime_registered_date=_parse_date(case.get("registered_date")),
                police_person_id=officer.employee_id if officer else None,
                police_station_id=int(case["police_station_id"]),
                case_category_id=category_by_code[
                    str(case["category_code"])
                ].case_category_id,
                gravity_offence_id=gravity.gravity_offence_id if gravity else None,
                crime_major_head_id=major.crime_head_id if major else None,
                crime_minor_head_id=minor.crime_sub_head_id if minor else None,
                case_status_id=status_map[case["status"]].case_status_id,
                court_id=court.court_id if court else None,
                incident_from_date=_parse_dt(case.get("incident_from")),
                incident_to_date=_parse_dt(case.get("incident_to")),
                info_received_ps_date=_parse_dt(case.get("info_received")),
                latitude=(
                    Decimal(str(case["latitude"])) if case.get("latitude") else None
                ),
                longitude=(
                    Decimal(str(case["longitude"])) if case.get("longitude") else None
                ),
                brief_facts=case.get("brief_facts"),
                victims=[
                    Victim(
                        victim_name=v["name"],
                        age_year=v.get("age_year"),
                        gender_id=v.get("gender_id"),
                        victim_police=v.get("victim_police", "0"),
                    )
                    for v in case.get("victims") or []
                ],
                accused=[
                    Accused(
                        accused_name=a["name"],
                        age_year=a.get("age_year"),
                        gender_id=a.get("gender_id"),
                        person_id=a.get("person_id"),
                    )
                    for a in case.get("accused") or []
                ],
                complainants=[
                    ComplainantDetails(
                        complainant_name=c["name"],
                        age_year=c.get("age_year"),
                        gender_id=c.get("gender_id"),
                        occupation_id=(
                            occ_map[c["occupation"]].occupation_id
                            if c.get("occupation") in occ_map
                            else None
                        ),
                        religion_id=(
                            rel_map[c["religion"]].religion_id
                            if c.get("religion") in rel_map
                            else None
                        ),
                        caste_id=(
                            caste_map[c["caste"]].caste_master_id
                            if c.get("caste") in caste_map
                            else None
                        ),
                    )
                    for c in case.get("complainants") or []
                ],
                act_sections=[
                    ActSectionAssociation(
                        act_id=s["act_id"],
                        section_id=str(s["section_id"]),
                        act_order_id=int(s.get("act_order_id") or 1),
                        section_order_id=int(s.get("section_order_id") or 1),
                    )
                    for s in case.get("act_sections") or []
                ],
            )
            occ = case.get("occurrence")
            if occ:
                entity.occurrence = InvOccuranceTime(
                    occurrence_from=_parse_dt(occ.get("occurrence_from")),
                    occurrence_to=_parse_dt(occ.get("occurrence_to")),
                    place_of_occurrence=occ.get("place_of_occurrence"),
                    beat_number=occ.get("beat_number"),
                    distance_from_ps_km=(
                        Decimal(str(occ["distance_from_ps_km"]))
                        if occ.get("distance_from_ps_km") is not None
                        else None
                    ),
                    direction_from_ps=occ.get("direction_from_ps"),
                    village_or_city=occ.get("village_or_city"),
                )
            session.add(entity)
            session.flush()

            accused_by_person = {
                (a.person_id or ""): a.accused_master_id for a in entity.accused
            }
            for ar in case.get("arrests") or []:
                aid = accused_by_person.get(str(ar.get("accused_person_id") or ""))
                io = emp_map.get(ar.get("io") or "")
                ar_court = court_map.get(ar.get("court") or "")
                arrest = ArrestSurrender(
                    case_master_id=entity.case_master_id,
                    arrest_surrender_type_id=int(ar.get("type_id") or 1),
                    arrest_surrender_date=_parse_date(ar.get("date")),
                    arrest_surrender_state_id=state.state_id,
                    arrest_surrender_district_id=int(case["district_id"]),
                    police_station_id=int(case["police_station_id"]),
                    io_id=io.employee_id if io else None,
                    court_id=ar_court.court_id if ar_court else None,
                    accused_master_id=aid,
                    is_accused=bool(ar.get("is_accused", True)),
                )
                if aid:
                    arrest.accused_links = [
                        InvArrestSurrenderAccused(accused_master_id=aid)
                    ]
                session.add(arrest)

            cs = case.get("chargesheet")
            if cs:
                cs_officer = emp_map.get(cs.get("police_person") or "")
                session.add(
                    ChargesheetDetails(
                        case_master_id=entity.case_master_id,
                        cs_date=_parse_dt(cs.get("cs_date")),
                        cs_type=str(cs.get("cs_type") or "A"),
                        police_person_id=(
                            cs_officer.employee_id if cs_officer else None
                        ),
                    )
                )

        session.commit()
        print(
            f"postgres: seeded {len(cases)} FIRs + occurrence/arrests/chargesheets/"
            f"courts/employees"
        )
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed FIR ER demo dataset")
    parser.add_argument(
        "--target",
        choices=("both", "postgres", "catalyst-mock"),
        default="both",
    )
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=None,
        help="YAML dataset path (default: fir_full_dataset.yaml if present, else fir_demo)",
    )
    args = parser.parse_args()

    dataset_path = args.dataset
    if dataset_path is None:
        dataset_path = FULL_DATASET_PATH if FULL_DATASET_PATH.exists() else DATASET_PATH

    data = load_dataset(dataset_path)
    cases = enrich_cases(data)
    print(f"dataset: {len(cases)} cases from {dataset_path}")

    if args.target in {"both", "catalyst-mock"}:
        export_catalyst_mock(data)
        export_rag_documents(data)
        export_ai_features(data)
        export_lookups(data)
    if args.target in {"both", "postgres"}:
        seed_postgres(data, force=args.force)


if __name__ == "__main__":
    main()
