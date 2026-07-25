#!/usr/bin/env python3
"""Generate synthetic FIRs covering all 31 Karnataka districts.

Writes database/seed/fir_statewide_karnataka.yaml — merged by seed_fir_dataset.py.
Accused / victims use realistic Kannada-region names for network & case viz.

Usage:
  python database/seed/generate_statewide_karnataka.py
  PYTHONPATH=backend python database/seed/seed_fir_dataset.py --target catalyst-mock --force
"""

from __future__ import annotations

from pathlib import Path

import yaml

OUT = Path(__file__).resolve().parent / "fir_statewide_karnataka.yaml"

KARNATAKA_DISTRICTS: list[tuple[str, float, float]] = [
    ("Bagalkote", 16.1867, 75.6961),
    ("Ballari", 15.1394, 76.9214),
    ("Belagavi", 15.8497, 74.4977),
    ("Bengaluru Rural", 13.2846, 77.5950),
    ("Bengaluru Urban", 12.9716, 77.5946),
    ("Bidar", 17.9104, 77.5199),
    ("Chamarajanagara", 11.9261, 76.9437),
    ("Chikkaballapur", 13.4355, 77.7315),
    ("Chikkamagaluru", 13.3161, 75.7720),
    ("Chitradurga", 14.2253, 76.3980),
    ("Dakshina Kannada", 12.9141, 74.8560),
    ("Davanagere", 14.4644, 75.9218),
    ("Dharwad", 15.4589, 75.0078),
    ("Gadag", 15.4315, 75.6350),
    ("Hassan", 13.0033, 76.1004),
    ("Haveri", 14.7936, 75.3990),
    ("Kalaburagi", 17.3297, 76.8343),
    ("Kodagu", 12.4244, 75.7382),
    ("Kolar", 13.1367, 78.1291),
    ("Koppal", 15.3452, 76.1548),
    ("Mandya", 12.5242, 76.8970),
    ("Mysuru", 12.2958, 76.6394),
    ("Raichur", 16.2076, 77.3463),
    ("Ramanagara", 12.7209, 77.2824),
    ("Shivamogga", 13.9299, 75.5681),
    ("Tumakuru", 13.3379, 77.1173),
    ("Udupi", 13.3409, 74.7421),
    ("Uttara Kannada", 14.8136, 74.1300),
    ("Vijayanagara", 15.2700, 76.3900),
    ("Vijayapura", 16.8302, 75.7100),
    ("Yadgir", 16.7717, 77.1376),
]

assert len(KARNATAKA_DISTRICTS) == 31

# Recurring personas → stable person_id for link analysis
RING = {
    "fraud": {"name": "Ramesh Nayak", "person_id": "SWFRAUD", "age": 34, "gender": "M"},
    "assault_link": {
        "name": "Imran Pasha",
        "person_id": "SWLINK",
        "age": 29,
        "gender": "M",
    },
    "helper": {"name": "Bhaskar Hegde", "person_id": "H2", "age": 22, "gender": "M"},
}

MALE_FIRST = [
    "Anand",
    "Basavaraj",
    "Chetan",
    "Deepak",
    "Eshwar",
    "Ganesh",
    "Harish",
    "Jagadish",
    "Kiran",
    "Lokesh",
    "Mahesh",
    "Nagesh",
    "Prakash",
    "Ravi",
    "Suresh",
    "Umesh",
    "Vijay",
    "Yogesh",
    "Naveen",
    "Sanjay",
    "Manjunath",
    "Shivaraj",
    "Praveen",
    "Dinesh",
    "Raghavendra",
    "Satish",
    "Ashok",
    "Vinod",
]
FEMALE_FIRST = [
    "Anitha",
    "Bhavya",
    "Deepa",
    "Geetha",
    "Kavitha",
    "Lakshmi",
    "Meena",
    "Poornima",
    "Rekha",
    "Shwetha",
    "Suma",
    "Vanitha",
    "Divya",
    "Priya",
]
SURNAMES = [
    "Gowda",
    "Shetty",
    "Patil",
    "Nayak",
    "Hegde",
    "Rao",
    "Reddy",
    "Kulkarni",
    "Desai",
    "Joshi",
    "Bhat",
    "Kamath",
    "Poojary",
    "Naik",
    "Kamble",
    "Chavan",
    "Biradar",
    "Hiremath",
    "Bannur",
    "Uppin",
]

VICTIM_MALE = [
    "Venkatappa",
    "Krishnamurthy",
    "Shankara",
    "Hanumanthappa",
    "Rajashekar",
    "Mahadeva",
    "Siddarama",
    "Thimmaiah",
    "Narayana",
    "Govindaraju",
]
VICTIM_FEMALE = [
    "Kamalamma",
    "Saraswathi",
    "Parvathi",
    "Gangamma",
    "Rathnamma",
    "Jayalakshmi",
    "Pushpa",
    "Savitha",
    "Nirmala",
    "Bhagyalakshmi",
]


def _person(i: int, j: int, role: str) -> dict:
    """District-local accused with unique person_id."""
    first = MALE_FIRST[(i * 3 + j) % len(MALE_FIRST)]
    surname = SURNAMES[(i * 5 + j * 2) % len(SURNAMES)]
    return {
        "name": f"{first} {surname}",
        "age_year": 21 + ((i * 4 + j * 3) % 28),
        "gender_id": "M",
        "person_id": f"SW{i:02d}{role}",
    }


def _victim(i: int, j: int) -> dict:
    female = (i + j) % 3 == 0
    if female:
        first = VICTIM_FEMALE[(i + j) % len(VICTIM_FEMALE)]
        gender = "F"
    else:
        first = VICTIM_MALE[(i + j) % len(VICTIM_MALE)]
        gender = "M"
    surname = SURNAMES[(i + j * 3) % len(SURNAMES)]
    return {
        "name": f"{first} {surname}",
        "age_year": 28 + ((i + j * 5) % 35),
        "gender_id": gender,
        "victim_police": "0",
    }


def _complainant_from_victim(v: dict, i: int, j: int) -> dict:
    occ = ["trader", "employee", "farmer", "driver", "student"][(i + j) % 5]
    return {
        "name": v["name"],
        "age_year": v["age_year"],
        "gender_id": v["gender_id"],
        "occupation": occ,
        "religion": ["hindu", "muslim", "christian", "other"][(i + j) % 4],
        "caste": ["general", "obc", "sc", "st"][(i + j) % 4],
    }


CASE_TEMPLATES = [
    {
        "major_head": "property",
        "minor_head": "theft",
        "gravity": "non_heinous",
        "status": "ui",
        "section": "379",
        "facts": (
            "Two-wheeler theft near {place}. Accused {accused} (approx {age}y/{gender}) "
            "seen fleeing on bike; person id {pid}."
        ),
        "role": "TH",
        "ring": None,
        "co": None,
    },
    {
        "major_head": "body",
        "minor_head": "hurt",
        "gravity": "non_heinous",
        "status": "ui",
        "section": "323",
        "facts": (
            "Assault after altercation at {place} market. Accused {accused} with "
            "associate {co_name}; injuries documented."
        ),
        "role": "AS",
        "ring": None,
        "co": "assault_link",
    },
    {
        "major_head": "property",
        "minor_head": "cheating",
        "gravity": "non_heinous",
        "status": "cs",
        "section": "420",
        "facts": (
            "Online payment fraud from {place}. Primary accused {accused} linked to "
            "statewide mule pattern ({pid})."
        ),
        "role": "FR",
        "ring": "fraud",
        "co": None,
    },
    {
        "major_head": "property",
        "minor_head": "robbery",
        "gravity": "heinous",
        "status": "ui",
        "section": "392",
        "facts": (
            "Highway robbery attempt near {place}. Accused {accused} assisted by "
            "{co_name}; vehicle details under verification."
        ),
        "role": "RB",
        "ring": None,
        "co": "helper",
    },
]


def build() -> dict:
    districts = []
    units = []
    courts = []
    employees = []
    cases = []

    base_district_id = 2001
    base_circle_id = 5200
    base_ps_id = 5300

    for i, (name, lat, lon) in enumerate(KARNATAKA_DISTRICTS):
        did = base_district_id + i
        circle_id = base_circle_id + i
        ps_id = base_ps_id + i
        emp_key = f"e_sw_{did}_io"
        court_key = f"court_sw_{did}"
        place = f"{name} HQ"

        districts.append(
            {"id": did, "name": name, "hq_latitude": lat, "hq_longitude": lon}
        )
        units.append(
            {
                "id": circle_id,
                "name": f"{name} Circle",
                "district_id": did,
                "type": "circle",
                "type_key": "circle",
                "parent_unit": None,
            }
        )
        units.append(
            {
                "id": ps_id,
                "name": f"{name} Town PS",
                "district_id": did,
                "type_key": "ps",
                "parent_unit": circle_id,
            }
        )
        courts.append({"key": court_key, "name": f"JMFC {name}", "district_id": did})
        io_first = (
            FEMALE_FIRST[i % len(FEMALE_FIRST)]
            if i % 2
            else MALE_FIRST[i % len(MALE_FIRST)]
        )
        employees.append(
            {
                "key": emp_key,
                "kgid": f"KGIDSW{did}",
                "first_name": f"SI {io_first}",
                "unit_id": ps_id,
                "district_id": did,
                "rank": "si",
                "designation": "io",
                "gender_id": "F" if i % 2 else "M",
                "appointment_date": "2018-01-15",
            }
        )

        for j in range(3):
            tmpl = CASE_TEMPLATES[(i + j) % len(CASE_TEMPLATES)]
            month = 1 + ((i + j) % 12)
            day = 3 + ((i * 3 + j) % 25)
            lat_j = lat + (j - 1) * 0.02
            lon_j = lon + (j - 1) * 0.02

            if tmpl["ring"]:
                ring = RING[tmpl["ring"]]
                primary = {
                    "name": ring["name"],
                    "age_year": ring["age"],
                    "gender_id": ring["gender"],
                    "person_id": ring["person_id"],
                }
            else:
                primary = _person(i, j, tmpl["role"])

            accused_list = [primary]
            co_name = "—"
            if tmpl["co"]:
                co = RING[tmpl["co"]]
                accused_list.append(
                    {
                        "name": co["name"],
                        "age_year": co["age"] + (j % 3),
                        "gender_id": co["gender"],
                        "person_id": co["person_id"],
                    }
                )
                co_name = co["name"]

            victim = _victim(i, j)
            complainant = _complainant_from_victim(victim, i, j)

            facts = tmpl["facts"].format(
                place=place,
                district=name,
                accused=primary["name"],
                age=primary["age_year"],
                gender=primary["gender_id"],
                pid=primary["person_id"],
                co_name=co_name,
            )

            case = {
                "category_code": "1",
                "district_id": did,
                "police_station_id": ps_id,
                "year": 2026,
                "serial": 200 + j,
                "registered_date": f"2026-{month:02d}-{day:02d}",
                "status": tmpl["status"],
                "gravity": tmpl["gravity"],
                "major_head": tmpl["major_head"],
                "minor_head": tmpl["minor_head"],
                "incident_from": f"2026-{month:02d}-{day:02d}T18:00:00+00:00",
                "incident_to": f"2026-{month:02d}-{day:02d}T19:30:00+00:00",
                "info_received": f"2026-{month:02d}-{day:02d}T20:00:00+00:00",
                "latitude": f"{lat_j:.7f}",
                "longitude": f"{lon_j:.7f}",
                "brief_facts": facts,
                "complainants": [complainant],
                "victims": [victim],
                "accused": accused_list,
                "act_sections": [
                    {
                        "act_id": tmpl.get("act", "IPC"),
                        "section_id": str(tmpl["section"]),
                    }
                ],
                "registering_officer": emp_key,
                "court": court_key,
                "occurrence": {
                    "occurrence_from": f"2026-{month:02d}-{day:02d}T18:00:00+00:00",
                    "occurrence_to": f"2026-{month:02d}-{day:02d}T19:30:00+00:00",
                    "place_of_occurrence": place,
                    "beat_number": f"B-{j + 1:02d}",
                    "distance_from_ps_km": 0.5 + j * 0.3,
                    "direction_from_ps": ["N", "E", "S"][j],
                    "village_or_city": name,
                },
                "arrests": [
                    {
                        "type_id": 2,
                        "date": f"2026-{month:02d}-{min(day + 1, 28):02d}",
                        "accused_person_id": primary["person_id"],
                        "io": emp_key,
                        "court": court_key,
                        "is_accused": True,
                    }
                ],
            }
            if tmpl["status"] == "cs":
                case["chargesheets"] = [
                    {
                        "cs_type": "1",
                        "cs_date": f"2026-{min(month + 1, 12):02d}-15",
                        "officer": emp_key,
                    }
                ]
            cases.append(case)

    return {
        "_meta": {
            "source": "generate_statewide_karnataka.py",
            "districts": 31,
            "cases_per_district": 3,
            "accused_naming": "realistic_kannada_region",
            "note": "Synthetic statewide cover for all Karnataka districts",
        },
        "geography": {
            "districts": districts,
            "units": units,
            "courts": courts,
        },
        "personnel": {"employees": employees},
        "cases": cases,
    }


def main() -> None:
    payload = build()
    OUT.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )
    accused_names = {
        a["name"] for c in payload["cases"] for a in c.get("accused") or []
    }
    print(
        f"Wrote {OUT.name}: {len(payload['geography']['districts'])} districts, "
        f"{len(payload['cases'])} cases, {len(accused_names)} unique accused names"
    )


if __name__ == "__main__":
    main()
