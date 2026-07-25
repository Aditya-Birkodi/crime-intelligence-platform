"""Import KSP_Crime_Relational_Dataset.xlsx → YAML compatible with seed_fir_dataset.

Maps Excel relational sheets into FIR ER-shaped cases + masters.
Synthesizes 18-digit CrimeNo components (category/district/station/year/serial).

Usage (repo root):
  .venv/bin/python database/seed/import_ksp_xlsx.py
  .venv/bin/python database/seed/import_ksp_xlsx.py --merge  # curated + KSP → fir_full_dataset.yaml
"""

from __future__ import annotations

import argparse
import hashlib
import re
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any

import yaml

try:
    import openpyxl
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "openpyxl required: uv pip install openpyxl --python .venv/bin/python"
    ) from exc

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_XLSX = ROOT / "KSP_Crime_Relational_Dataset.xlsx"
OUT_KSP = Path(__file__).resolve().parent / "ksp_relational_dataset.yaml"
OUT_FULL = Path(__file__).resolve().parent / "fir_full_dataset.yaml"
CURATED = Path(__file__).resolve().parent / "fir_demo_dataset.yaml"
FEATURES_OUT = Path(__file__).resolve().parent / "ai_case_features.json"

# Avoid colliding with curated KSP-style district IDs (443+)
DISTRICT_ID_BASE = 1000
STATION_ID_BASE = 2000
CIRCLE_ID_BASE = 2100

_HEAD_MAP = {
    "Theft": ("property", "theft", "BNS", "303"),
    "Robbery": ("property", "robbery", "BNS", "309"),
    "Cyber Crime": ("cyber", "cyber_fraud", "IT", "66"),
    "Assault": ("body", "hurt", "BNS", "115"),
    "Fraud": ("property", "cheating", "BNS", "318"),
}

_STATUS_MAP = {
    "Open": "ui",
    "Under Investigation": "ui",
    "Charge Sheeted": "cs",
    "Closed": "closed",
}

_SEVERITY_MAP = {
    "High": "heinous",
    "Medium": "non_heinous",
    "Low": "non_heinous",
}


def _load_sheet(ws: Any) -> list[dict[str, Any]]:
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []
    header = [str(h) if h is not None else f"col{i}" for i, h in enumerate(rows[0])]
    out: list[dict[str, Any]] = []
    for row in rows[1:]:
        if row is None or all(v is None or str(v).strip() == "" for v in row):
            continue
        out.append(dict(zip(header, row, strict=False)))
    return out


def _gender(value: Any) -> str | None:
    text = str(value or "").strip().lower()
    if text.startswith("f"):
        return "F"
    if text.startswith("m"):
        return "M"
    return None


def _as_date(value: Any) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()[:10]
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _as_time(value: Any) -> time:
    if isinstance(value, datetime):
        return value.time()
    if isinstance(value, time):
        return value
    text = str(value or "00:00").strip()
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(text, fmt).time()
        except ValueError:
            continue
    return time(0, 0)


def _combine_dt(d: date | None, t: Any) -> str | None:
    if d is None:
        return None
    tt = _as_time(t)
    return datetime.combine(d, tt).isoformat()


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "x"


def _person_id(accused: dict[str, Any]) -> str:
    """Stable synthetic person id; cluster repeat offenders into mid-size hubs.

    Buckets by district + name so link graphs stay readable (~15–40 cases per hub)
    instead of collapsing every district into a single mega-node.
    """
    aid = int(accused["accused_id"])
    if accused.get("repeat_offender") in (True, "True", 1, "1"):
        district = str(accused.get("district") or "na")
        name = str(
            accused.get("name")
            or accused.get("accused_name")
            or accused.get("accused_id")
            or "x"
        ).lower()
        digest = hashlib.md5(f"{district}:{name}".encode()).hexdigest()
        bucket = int(digest[:6], 16) % 36
        return f"KR{bucket:02d}"
    return f"K{aid:04d}"


def import_workbook(path: Path) -> dict[str, Any]:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    districts = _load_sheet(wb["District"])
    stations = _load_sheet(wb["PoliceStation"])
    heads = _load_sheet(wb["CrimeHead"])
    subs = _load_sheet(wb["CrimeSubHead"])
    acts = _load_sheet(wb["Acts"])
    sections = _load_sheet(wb["Sections"])
    officers = _load_sheet(wb["Officer"])
    cases = _load_sheet(wb["CaseMaster"])
    accused_rows = _load_sheet(wb["Accused"])
    victims = _load_sheet(wb["Victim"])
    complainants = _load_sheet(wb["Complainant"])
    wb.close()

    dist_name_to_id = {
        str(d["district_name"]): DISTRICT_ID_BASE + int(d["district_id"])
        for d in districts
    }
    dist_excel_to_cip = {
        int(d["district_id"]): DISTRICT_ID_BASE + int(d["district_id"])
        for d in districts
    }
    st_excel_to_cip = {
        int(s["police_station_id"]): STATION_ID_BASE + int(s["police_station_id"])
        for s in stations
    }

    head_name = {int(h["crime_head_id"]): str(h["crime_head"]) for h in heads}
    sub_name = {int(s["crime_sub_head_id"]): str(s["crime_sub_head"]) for s in subs}
    act_name = {int(a["act_id"]): str(a["act_name"]) for a in acts}
    act_code = {
        i: (
            "BNS"
            if "bns" in n.lower()
            else (
                "IT"
                if "it" in n.lower()
                else "NDPS" if "ndps" in n.lower() else _slug(n).upper()[:10]
            )
        )
        for i, n in act_name.items()
    }
    section_by_act: dict[int, list[dict[str, Any]]] = {}
    for s in sections:
        section_by_act.setdefault(int(s["act_id"]), []).append(s)

    accused_by_case: dict[int, list[dict[str, Any]]] = {}
    for a in accused_rows:
        accused_by_case.setdefault(int(a["case_id"]), []).append(a)
    victims_by_case: dict[int, list[dict[str, Any]]] = {}
    for v in victims:
        victims_by_case.setdefault(int(v["case_id"]), []).append(v)
    complainants_by_case: dict[int, list[dict[str, Any]]] = {}
    for c in complainants:
        complainants_by_case.setdefault(int(c["case_id"]), []).append(c)

    # Geography
    unit_rows: list[dict[str, Any]] = []
    stations_by_district: dict[int, list[dict[str, Any]]] = {}
    for s in stations:
        dname = str(s["district"])
        did = dist_name_to_id.get(dname)
        if did is None:
            # fallback: first district
            did = next(iter(dist_excel_to_cip.values()))
        stations_by_district.setdefault(did, []).append(s)

    for did, group in stations_by_district.items():
        circle_id = CIRCLE_ID_BASE + (did - DISTRICT_ID_BASE)
        unit_rows.append(
            {
                "id": circle_id,
                "name": f"Circle {did}",
                "district_id": did,
                "type_key": "circle",
                "parent_unit": None,
            }
        )
        for s in group:
            sid = st_excel_to_cip[int(s["police_station_id"])]
            unit_rows.append(
                {
                    "id": sid,
                    "name": str(s["police_station_name"]),
                    "district_id": did,
                    "type_key": "ps",
                    "parent_unit": circle_id,
                    "latitude": float(s["latitude"]) if s.get("latitude") else None,
                    "longitude": float(s["longitude"]) if s.get("longitude") else None,
                }
            )

    emp_keys: dict[int, str] = {}
    employees: list[dict[str, Any]] = []
    rank_keys = {
        "pi": "inspector",
        "psi": "si",
        "hc": "constable",
        "pc": "constable",
        "asi": "asi",
        "inspector": "inspector",
        "si": "si",
        "constable": "constable",
    }
    for o in officers:
        oid = int(o["officer_id"])
        key = f"ksp_off_{oid}"
        emp_keys[oid] = key
        rank_raw = str(o.get("rank") or "PC").lower()
        rank = rank_keys.get(rank_raw, "constable")
        st = st_excel_to_cip.get(int(o["station_id"]))
        # find district for station
        did = None
        for u in unit_rows:
            if u["id"] == st:
                did = u["district_id"]
                break
        employees.append(
            {
                "key": key,
                "district_id": did or next(iter(dist_excel_to_cip.values())),
                "unit_id": st or next(iter(st_excel_to_cip.values())),
                "rank": rank,
                "designation": "io",
                "kgid": str(o.get("badge_number") or f"KSP{oid:04d}"),
                "first_name": str(o.get("name") or f"Officer {oid}"),
                "gender_id": "M",
                "appointment_date": "2010-01-01",
            }
        )

    legal_acts = []
    seen_acts: set[str] = set()
    for aid, code in act_code.items():
        if code in seen_acts:
            continue
        seen_acts.add(code)
        legal_acts.append(
            {
                "code": code,
                "description": act_name[aid],
                "short_name": code,
            }
        )
    # ensure BNS/IT/NDPS present
    for code, desc in (
        ("BNS", "Bharatiya Nyaya Sanhita"),
        ("IT", "IT Act"),
        ("NDPS", "NDPS Act"),
    ):
        if code not in seen_acts:
            legal_acts.append({"code": code, "description": desc, "short_name": code})

    legal_sections: list[dict[str, Any]] = []
    seen_sec: set[tuple[str, str]] = set()
    for s in sections:
        code = act_code[int(s["act_id"])]
        sec = str(s["section_number"])
        if (code, sec) in seen_sec:
            continue
        seen_sec.add((code, sec))
        legal_sections.append(
            {
                "act_code": code,
                "code": sec,
                "description": str(s.get("section_description") or sec),
            }
        )
    # defaults from head map
    for _, _, ac, sc in _HEAD_MAP.values():
        if (ac, sc) not in seen_sec:
            seen_sec.add((ac, sc))
            legal_sections.append(
                {"act_code": ac, "code": sc, "description": f"Section {sc}"}
            )

    crime_heads_yaml = [
        {
            "key": "body",
            "group_name": "Crimes Against Body",
            "sub_heads": [{"key": "hurt", "name": "Hurt / Assault", "seq_id": 1}],
        },
        {
            "key": "property",
            "group_name": "Crimes Against Property",
            "sub_heads": [
                {"key": "theft", "name": "Theft", "seq_id": 1},
                {"key": "robbery", "name": "Robbery", "seq_id": 2},
                {"key": "cheating", "name": "Cheating / Fraud", "seq_id": 3},
            ],
        },
        {
            "key": "cyber",
            "group_name": "Cyber Crime",
            "sub_heads": [
                {"key": "cyber_fraud", "name": "Cyber Fraud", "seq_id": 1},
            ],
        },
    ]

    chas = [
        {"major_head": "property", "act_code": "BNS", "section_code": "303"},
        {"major_head": "property", "act_code": "BNS", "section_code": "309"},
        {"major_head": "property", "act_code": "BNS", "section_code": "318"},
        {"major_head": "body", "act_code": "BNS", "section_code": "115"},
        {"major_head": "cyber", "act_code": "IT", "section_code": "66"},
    ]

    courts = []
    for i in range(1, 11):
        courts.append(
            {
                "key": f"ksp_court_{i}",
                "name": f"KSP Court {i}",
                "district_id": next(iter(dist_excel_to_cip.values())),
            }
        )

    out_cases: list[dict[str, Any]] = []
    features: list[dict[str, Any]] = []

    for c in cases:
        cid = int(c["case_id"])
        fir_date = _as_date(c.get("fir_date")) or date(2025, 1, 1)
        occ_date = _as_date(c.get("occurrence_date")) or fir_date
        excel_dist = int(c["district_id"])
        excel_st = int(c["police_station_id"])
        district_id = dist_excel_to_cip[excel_dist]
        station_id = st_excel_to_cip[excel_st]
        head = head_name.get(int(c["crime_head_id"]), "Theft")
        major, minor, act_code_s, sec_code = _HEAD_MAP.get(
            head, ("property", "theft", "BNS", "303")
        )
        status = _STATUS_MAP.get(str(c.get("investigation_status") or "Open"), "ui")
        gravity = _SEVERITY_MAP.get(str(c.get("severity") or "Medium"), "non_heinous")
        io_key = emp_keys.get(int(c["investigating_officer_id"]))
        court_key = f"ksp_court_{int(c.get('court_id') or 1)}"

        # jitter coords from identical 12.9/77.6 using case id
        base_lat = float(c.get("latitude") or 12.9)
        base_lon = float(c.get("longitude") or 77.6)
        lat = round(base_lat + ((cid % 17) - 8) * 0.012, 6)
        lon = round(base_lon + ((cid % 13) - 6) * 0.014, 6)
        # prefer station coords if available
        for u in unit_rows:
            if u["id"] == station_id and u.get("latitude") is not None:
                lat = round(float(u["latitude"]) + ((cid % 7) - 3) * 0.008, 6)
                lon = round(float(u["longitude"]) + ((cid % 5) - 2) * 0.008, 6)
                break

        mo = str(c.get("modus_operandi") or "").strip()
        summary = str(c.get("case_summary") or "").strip()
        place = str(c.get("place_of_occurrence") or f"Location {cid}")
        sub = sub_name.get(int(c["crime_sub_head_id"]), "")
        brief = (
            f"{summary}. MO: {mo}. Place: {place}. "
            f"Head: {head}/{sub}. Severity: {c.get('severity')}. "
            f"RiskScore: {int(c.get('risk_score') or 0)}. "
            f"Source FIR: {c.get('fir_number')}."
        )

        case_accused = []
        arrests = []
        for a in accused_by_case.get(cid, []):
            pid = _person_id(a)
            case_accused.append(
                {
                    "name": str(a.get("name") or "Accused"),
                    "age_year": int(a["age"]) if a.get("age") is not None else None,
                    "gender_id": _gender(a.get("gender")),
                    "person_id": pid,
                }
            )
            if str(a.get("arrest_status") or "").lower().startswith("arrest"):
                ad = _as_date(a.get("arrest_date")) or fir_date
                arrests.append(
                    {
                        "type_id": 1,
                        "date": ad.isoformat(),
                        "accused_person_id": pid,
                        "io": io_key,
                        "court": court_key,
                        "is_accused": True,
                    }
                )

        case_victims = [
            {
                "name": str(v.get("name") or "Victim"),
                "age_year": int(v["age"]) if v.get("age") is not None else None,
                "gender_id": _gender(v.get("gender")),
                "victim_police": "0",
            }
            for v in victims_by_case.get(cid, [])
        ] or [
            {
                "name": "Unknown Victim",
                "age_year": None,
                "gender_id": None,
                "victim_police": "0",
            }
        ]

        case_complainants = [
            {
                "name": str(cp.get("name") or "Complainant"),
                "age_year": None,
                "gender_id": None,
                "occupation": "employee",
                "religion": "other",
                "caste": "general",
            }
            for cp in complainants_by_case.get(cid, [])
        ] or [
            {
                "name": "Complainant",
                "age_year": None,
                "gender_id": None,
                "occupation": "employee",
                "religion": "other",
                "caste": "general",
            }
        ]

        occ_from = _combine_dt(occ_date, c.get("occurrence_time"))
        occ_to = (
            (datetime.fromisoformat(occ_from) + timedelta(hours=1)).isoformat()
            if occ_from
            else None
        )

        cs_status = str(c.get("chargesheet_status") or "Pending").lower()
        chargesheet = None
        if cs_status not in {"pending", "nil", ""}:
            chargesheet = {
                "cs_date": (fir_date + timedelta(days=30)).isoformat(),
                "cs_type": "A",
                "police_person": io_key,
            }
            status = "cs"

        out_cases.append(
            {
                "category_code": "1",
                "district_id": district_id,
                "police_station_id": station_id,
                "year": fir_date.year,
                "serial": cid,  # unique within import set
                "registered_date": fir_date.isoformat(),
                "status": status,
                "gravity": gravity,
                "major_head": major,
                "minor_head": minor,
                "incident_from": occ_from,
                "incident_to": occ_to,
                "info_received": _combine_dt(fir_date, c.get("fir_time")),
                "latitude": lat,
                "longitude": lon,
                "brief_facts": brief,
                "complainants": case_complainants,
                "victims": case_victims,
                "accused": case_accused,
                "act_sections": [{"act_id": act_code_s, "section_id": sec_code}],
                "registering_officer": io_key,
                "court": court_key,
                "occurrence": {
                    "occurrence_from": occ_from,
                    "occurrence_to": occ_to,
                    "place_of_occurrence": place,
                    "beat_number": str((cid % 9) + 1),
                    "distance_from_ps_km": round(0.5 + (cid % 10) * 0.3, 2),
                    "direction_from_ps": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"][
                        cid % 8
                    ],
                    "village_or_city": place,
                },
                "arrests": arrests,
                **({"chargesheet": chargesheet} if chargesheet else {}),
                "_source": "ksp_xlsx",
                "_fir_number": str(c.get("fir_number")),
                "_risk_score": int(c.get("risk_score") or 0),
                "_severity": str(c.get("severity") or ""),
                "_modus_operandi": mo,
            }
        )
        features.append(
            {
                "source": "ksp_xlsx",
                "fir_number": str(c.get("fir_number")),
                "serial": cid,
                "district_id": district_id,
                "police_station_id": station_id,
                "year": fir_date.year,
                "risk_score": int(c.get("risk_score") or 0),
                "severity": str(c.get("severity") or ""),
                "modus_operandi": mo,
                "crime_head": head,
                "chargesheet_status": str(c.get("chargesheet_status") or ""),
            }
        )

    dataset: dict[str, Any] = {
        "masters": {
            "case_statuses": [
                {"key": "ui", "name": "Under Investigation"},
                {"key": "cs", "name": "Charge Sheeted"},
                {"key": "closed", "name": "Closed"},
            ],
            "case_categories": [
                {"key": "fir", "lookup_value": "FIR", "category_code": "1"},
                {"key": "udr", "lookup_value": "UDR", "category_code": "3"},
                {"key": "par", "lookup_value": "PAR", "category_code": "4"},
                {"key": "zero_fir", "lookup_value": "Zero FIR", "category_code": "8"},
            ],
            "gravity_offences": [
                {"key": "heinous", "lookup_value": "Heinous"},
                {"key": "non_heinous", "lookup_value": "Non-Heinous"},
            ],
            "occupations": [
                {"key": "trader", "name": "Trader"},
                {"key": "employee", "name": "Private Employee"},
                {"key": "student", "name": "Student"},
                {"key": "farmer", "name": "Farmer"},
                {"key": "driver", "name": "Driver"},
            ],
            "religions": [
                {"key": "hindu", "name": "Hindu"},
                {"key": "muslim", "name": "Muslim"},
                {"key": "christian", "name": "Christian"},
                {"key": "other", "name": "Other"},
            ],
            "castes": [
                {"key": "general", "name": "General"},
                {"key": "obc", "name": "OBC"},
                {"key": "sc", "name": "SC"},
                {"key": "st", "name": "ST"},
            ],
        },
        "geography": {
            "state": {"name": "Karnataka", "active": True},
            "districts": [
                {
                    "id": dist_excel_to_cip[int(d["district_id"])],
                    "name": str(d["district_name"]),
                    "population": d.get("population"),
                    "literacy_rate": d.get("literacy_rate"),
                    "urbanization_index": d.get("urbanization_index"),
                    "unemployment_rate": d.get("unemployment_rate"),
                    "poverty_index": d.get("poverty_index"),
                }
                for d in districts
            ],
            "unit_type": {
                "name": "Police Station",
                "city_dist_state": "City",
                "hierarchy": 1,
            },
            "unit_types": [
                {
                    "key": "ps",
                    "name": "Police Station",
                    "city_dist_state": "City",
                    "hierarchy": 1,
                },
                {
                    "key": "circle",
                    "name": "Circle Office",
                    "city_dist_state": "City",
                    "hierarchy": 2,
                },
            ],
            "units": unit_rows,
            "courts": courts,
        },
        "legal": {
            "acts": legal_acts,
            "sections": legal_sections,
            "crime_heads": crime_heads_yaml,
            "crime_head_act_sections": chas,
        },
        "personnel": {
            "ranks": [
                {"key": "pi", "name": "Police Inspector", "hierarchy": 5},
                {"key": "psi", "name": "PSI", "hierarchy": 4},
                {"key": "asi", "name": "ASI", "hierarchy": 3},
                {"key": "hc", "name": "Head Constable", "hierarchy": 2},
                {"key": "pc", "name": "Police Constable", "hierarchy": 1},
            ],
            "designations": [
                {"key": "io", "name": "Investigating Officer", "sort_order": 1},
                {"key": "sho", "name": "SHO", "sort_order": 2},
            ],
            "employees": employees,
        },
        "cases": out_cases,
        "_ai_features": features,
        "_meta": {
            "source": str(path.name),
            "case_count": len(out_cases),
            "district_id_base": DISTRICT_ID_BASE,
            "station_id_base": STATION_ID_BASE,
        },
    }
    return dataset


def _dedupe_sections(a: list[Any], b: list[Any]) -> list[Any]:
    seen: set[tuple[str, str]] = set()
    out: list[Any] = []
    for item in list(a) + list(b):
        if not isinstance(item, dict):
            continue
        pair = (str(item.get("act_code")), str(item.get("code")))
        if pair in seen:
            continue
        seen.add(pair)
        out.append(item)
    return out


def _merge_lists(
    a: list[Any],
    b: list[Any],
    *,
    key: str | None = None,
    also_unique: str | None = None,
) -> list[Any]:
    if key is None:
        return list(a) + list(b)
    seen: set[Any] = set()
    seen_alt: set[Any] = set()
    out: list[Any] = []
    for item in list(a) + list(b):
        if not isinstance(item, dict):
            out.append(item)
            continue
        k = item.get(key)
        alt = item.get(also_unique) if also_unique else None
        if k in seen:
            continue
        if alt is not None and alt in seen_alt:
            continue
        if k is not None:
            seen.add(k)
        if alt is not None:
            seen_alt.add(alt)
        out.append(item)
    return out


def merge_datasets(curated: dict[str, Any], ksp: dict[str, Any]) -> dict[str, Any]:
    """Merge curated demo + KSP import (masters union, cases concatenated)."""
    geo_c = curated.get("geography") or {}
    geo_k = ksp.get("geography") or {}
    legal_c = curated.get("legal") or {}
    legal_k = ksp.get("legal") or {}
    pers_c = curated.get("personnel") or {}
    pers_k = ksp.get("personnel") or {}
    masters_c = curated.get("masters") or {}
    masters_k = ksp.get("masters") or {}

    # strip importer-only keys from cases
    ksp_cases = []
    for case in ksp.get("cases") or []:
        clean = {k: v for k, v in case.items() if not k.startswith("_")}
        ksp_cases.append(clean)

    merged = {
        "masters": {
            "case_statuses": _merge_lists(
                masters_c.get("case_statuses") or [],
                masters_k.get("case_statuses") or [],
                key="key",
            ),
            "case_categories": _merge_lists(
                masters_c.get("case_categories") or [],
                masters_k.get("case_categories") or [],
                key="key",
            ),
            "gravity_offences": _merge_lists(
                masters_c.get("gravity_offences") or [],
                masters_k.get("gravity_offences") or [],
                key="key",
            ),
            "occupations": _merge_lists(
                masters_c.get("occupations") or [],
                masters_k.get("occupations") or [],
                key="key",
            ),
            "religions": _merge_lists(
                masters_c.get("religions") or [],
                masters_k.get("religions") or [],
                key="key",
            ),
            "castes": _merge_lists(
                masters_c.get("castes") or [], masters_k.get("castes") or [], key="key"
            ),
        },
        "geography": {
            "state": geo_c.get("state") or geo_k.get("state"),
            "districts": _merge_lists(
                geo_c.get("districts") or [], geo_k.get("districts") or [], key="id"
            ),
            "unit_type": geo_c.get("unit_type") or geo_k.get("unit_type"),
            "unit_types": _merge_lists(
                geo_c.get("unit_types") or [],
                geo_k.get("unit_types") or [],
                key="key",
            ),
            "units": _merge_lists(
                geo_c.get("units") or [], geo_k.get("units") or [], key="id"
            ),
            "courts": _merge_lists(
                geo_c.get("courts") or [], geo_k.get("courts") or [], key="key"
            ),
        },
        "legal": {
            "acts": _merge_lists(
                legal_c.get("acts") or [], legal_k.get("acts") or [], key="code"
            ),
            "sections": _dedupe_sections(
                legal_c.get("sections") or [], legal_k.get("sections") or []
            ),
            "crime_heads": _merge_lists(
                legal_c.get("crime_heads") or [],
                legal_k.get("crime_heads") or [],
                key="key",
            ),
            "crime_head_act_sections": _merge_lists(
                legal_c.get("crime_head_act_sections") or [],
                legal_k.get("crime_head_act_sections") or [],
            ),
        },
        "personnel": {
            # Prefer curated rank/designation catalog; KSP employees remap onto these keys.
            "ranks": list(pers_c.get("ranks") or pers_k.get("ranks") or []),
            "designations": list(
                pers_c.get("designations") or pers_k.get("designations") or []
            ),
            "employees": _merge_lists(
                pers_c.get("employees") or [],
                pers_k.get("employees") or [],
                key="key",
            ),
        },
        "cases": list(curated.get("cases") or []) + ksp_cases,
        "_ai_features": list(ksp.get("_ai_features") or []),
        "_meta": {
            "merged_from": ["fir_demo_dataset.yaml", "ksp_relational_dataset.yaml"],
            "curated_cases": len(curated.get("cases") or []),
            "ksp_cases": len(ksp_cases),
        },
    }
    return merged


def _dump_yaml(data: dict[str, Any], path: Path) -> None:
    # drop heavy internal-only when writing seedable yaml
    payload = {k: v for k, v in data.items() if k not in {"_ai_features"}}
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Import KSP relational Excel dataset")
    parser.add_argument("--xlsx", type=Path, default=DEFAULT_XLSX)
    parser.add_argument("--out", type=Path, default=OUT_KSP)
    parser.add_argument(
        "--merge",
        action="store_true",
        help=f"Also write merged curated+KSP dataset to {OUT_FULL.name}",
    )
    parser.add_argument("--curated", type=Path, default=CURATED)
    args = parser.parse_args()

    if not args.xlsx.exists():
        raise SystemExit(f"Excel not found: {args.xlsx}")

    ksp = import_workbook(args.xlsx)
    _dump_yaml(ksp, args.out)
    # features sidecar for B4
    import json

    FEATURES_OUT.write_text(
        json.dumps(ksp.get("_ai_features") or [], indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"ksp-import: {len(ksp.get('cases') or [])} cases → {args.out} "
        f"(features → {FEATURES_OUT})"
    )

    if args.merge:
        curated = yaml.safe_load(args.curated.read_text(encoding="utf-8"))
        if not isinstance(curated, dict):
            raise SystemExit(f"Invalid curated dataset: {args.curated}")
        full = merge_datasets(curated, ksp)
        _dump_yaml(full, OUT_FULL)
        print(
            f"merged: {full['_meta']['curated_cases']} curated + "
            f"{full['_meta']['ksp_cases']} ksp → {OUT_FULL} "
            f"(total cases {len(full['cases'])})"
        )


if __name__ == "__main__":
    main()
