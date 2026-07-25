#!/usr/bin/env python3
"""Seed Catalyst Data Store via CLI CSV import (uses logged-in catalyst CLI).

Flow:
  1. Write CSVs from appsail_datastore.json
  2. catalyst ds:import → cip_case_master
  3. catalyst ds:export + download → crime_no → live ROWID map
  4. Import children with remapped case_master_id (and accused ROWIDs for arrests)

Usage:
  python database/seed/seed_catalyst_via_cli.py --limit 5
  python database/seed/seed_catalyst_via_cli.py --force   # full seed (dev max 5000/table)
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import time
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).resolve().parent / "appsail_datastore.json"
OUT = ROOT / ".data" / "catalyst_cli_seed"
LOOKUPS = Path(__file__).resolve().parent / "appsail_lookups.json"

_SYSTEM = {"ROWID", "CREATORID", "CREATEDTIME", "MODIFIEDTIME"}


def _run(cmd: list[str], *, input_text: str | None = None) -> str:
    print("+", " ".join(cmd))
    env = {k: v for k, v in __import__("os").environ.items()}
    # Interactive bucket select needs a real TTY answer — feed "aditya"
    if input_text is None and "ds:import" in cmd:
        input_text = "aditya\n/\nn\n"
    proc = subprocess.run(
        cmd,
        input=input_text,
        text=True,
        capture_output=True,
        cwd=str(ROOT),
        env=env,
        check=False,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    print(out[-2000:] if len(out) > 2000 else out)
    if "Successfully scheduled" not in out and proc.returncode != 0:
        raise RuntimeError(f"Command failed ({proc.returncode}): {cmd}\n{out}")
    return out


def _job_id(out: str) -> str:
    m = re.search(r'jobid ["\']?(\d+)', out, re.I)
    if not m:
        m = re.search(r"job[_ ]?id[:\s\"]+(\d+)", out, re.I)
    if not m:
        raise RuntimeError(f"No job id in output:\n{out}")
    return m.group(1)


def _wait_import(job_id: str, timeout: int = 600) -> None:
    """Poll until Catalyst finishes the import job.

    When complete, the CLI prompts to download the report — that prompt is the
    reliable completion signal (status text often has no 'success' word).
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        # Answer "y" so we get the report zip for error inspection
        before = time.time()
        out = _run(
            ["catalyst", "ds:status", "import", job_id],
            input_text="y\n",
        )
        low = out.lower()
        if "fail" in low and "download the report" not in low:
            raise RuntimeError(f"Import job {job_id} failed:\n{out}")
        done = "download the report" in low or "success" in low or "completed" in low
        if done:
            # Inspect newest Import_*.zip for non-header error rows
            zips = sorted(
                [
                    p
                    for p in ROOT.glob("Import*.zip")
                    if p.stat().st_mtime >= before - 2
                ],
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if zips:
                _check_import_report(zips[0])
            return
        time.sleep(5)
    raise TimeoutError(f"Import job {job_id} timed out")


def _check_import_report(path: Path) -> None:
    try:
        with zipfile.ZipFile(path) as zf:
            for name in zf.namelist():
                if "ERROR" not in name.upper():
                    continue
                text = zf.read(name).decode("utf-8", errors="replace")
                rows = list(csv.DictReader(text.splitlines()))
                if rows:
                    sample = rows[0]
                    raise RuntimeError(
                        f"Import report has {len(rows)} error row(s) in {name}: {sample}"
                    )
                print(f"import report OK (0 errors): {path.name}")
    except zipfile.BadZipFile:
        print(f"WARN: could not read import report {path}")


def _export_and_download(table: str, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    # Ignore stale project-root exports from earlier jobs
    before = time.time()
    out = _run(
        ["catalyst", "ds:export", "--table", table, "--page", "1"],
        input_text=None,
    )
    jid = _job_id(out)
    deadline = time.time() + 600
    downloaded: Path | None = None
    while time.time() < deadline:
        proc = subprocess.run(
            ["catalyst", "ds:status", "export", jid],
            input="y\n",
            text=True,
            capture_output=True,
            cwd=str(ROOT),
            check=False,
        )
        text = (proc.stdout or "") + (proc.stderr or "")
        print(text[-1500:] if len(text) > 1500 else text)
        candidates = sorted(
            [
                p
                for p in list(ROOT.glob("*.zip")) + list(ROOT.glob("*.csv"))
                if p.stat().st_mtime >= before - 2
            ],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if candidates:
            target = dest_dir / candidates[0].name
            candidates[0].replace(target)
            downloaded = target
            break
        if "fail" in text.lower():
            raise RuntimeError(text)
        time.sleep(5)
    if downloaded is None:
        raise RuntimeError(f"Could not find export download for {table} job {jid}")
    # Brief settle; Catalyst sometimes finishes the zip before all rows flush
    time.sleep(2)
    return downloaded


def _fmt_value(v: Any) -> Any:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        # Catalyst DateTime columns reject ISO-8601 with T/+00:00
        if "T" in v and len(v) >= 19:
            # 2026-01-15T21:00:00+00:00 → 2026-01-15 21:00:00
            core = v.replace("T", " ")[:19]
            return core
        return v
    return v


def _write_csv(path: Path, rows: list[dict[str, Any]], cols: list[str]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        n = 0
        for row in rows:
            payload = {c: _fmt_value(row.get(c, "")) for c in cols}
            w.writerow(payload)
            n += 1
    print(f"wrote {n} rows → {path}")
    return n


def _load_tables() -> dict[str, list[dict[str, Any]]]:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    return payload["tables"]


def _pick(row: dict[str, Any], cols: list[str]) -> dict[str, Any]:
    return {c: row[c] for c in cols if c in row and row[c] is not None}


def _parse_export_csv(path: Path) -> list[dict[str, str]]:
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            names = [n for n in zf.namelist() if n.endswith(".csv")]
            if not names:
                raise RuntimeError(f"No CSV in zip {path}")
            with zf.open(names[0]) as raw:
                text = raw.read().decode("utf-8")
        rows = list(csv.DictReader(text.splitlines()))
        return rows
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _import_csv(table: str, csv_path: Path) -> None:
    # Stratus bucket prompt: bucket name → path → confirm overwrite
    out = _run(
        ["catalyst", "ds:import", str(csv_path), "--table", table],
        input_text="aditya\n/\nn\n",
    )
    jid = _job_id(out)
    _wait_import(jid)


def _unique_csv(name: str) -> Path:
    stamp = time.strftime("%Y%m%d%H%M%S")
    return OUT / f"{stamp}_{name}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument(
        "--skip-masters",
        action="store_true",
        help="Skip district/unit/status lookup tables",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip crime_nos already present in live cip_case_master",
    )
    parser.add_argument(
        "--children-only",
        action="store_true",
        help="Do not import cases; remap children using live crime_no→ROWID export",
    )
    parser.add_argument(
        "--skip-tables",
        nargs="*",
        default=[],
        help="Child table names to skip (e.g. cip_victim)",
    )
    parser.add_argument(
        "--masters-only",
        action="store_true",
        help="Only import district/unit/status master tables",
    )
    args = parser.parse_args()
    skip_tables = set(args.skip_tables or [])

    tables = _load_tables()
    cases = list(tables.get("cip_case_master") or [])
    if args.offset:
        cases = cases[args.offset :]
    if args.limit:
        cases = cases[: args.limit]

    OUT.mkdir(parents=True, exist_ok=True)

    if args.skip_existing and not args.children_only:
        print("Exporting live cases to skip existing crime_nos…")
        export_path = _export_and_download("cip_case_master", OUT / "exports")
        existing = {
            str(r.get("crime_no") or r.get("CRIME_NO") or "")
            for r in _parse_export_csv(export_path)
        }
        existing.discard("")
        before = len(cases)
        cases = [c for c in cases if str(c.get("crime_no")) not in existing]
        print(f"skip-existing: {before} → {len(cases)} cases ({len(existing)} live)")
        if not cases:
            print("Nothing new to import.")
            return 0

    allowed = {int(c["ROWID"]) for c in cases}

    # --- optional masters from lookups JSON ---
    if not args.skip_masters and LOOKUPS.exists():
        lookups = json.loads(LOOKUPS.read_text(encoding="utf-8"))
        # case statuses
        statuses = lookups.get("case_statuses") or []
        if statuses:
            rows = [
                {"case_status_id": r["id"], "case_status_name": r["name"]}
                for r in statuses
            ]
            p = _unique_csv("cip_case_status_master.csv")
            _write_csv(p, rows, ["case_status_id", "case_status_name"])
            _import_csv("cip_case_status_master", p)
        districts = lookups.get("districts") or []
        if districts:
            rows = [
                {
                    "district_id": r["id"],
                    "district_name": r["name"],
                    "state_id": 1,
                    "active": 1,
                }
                for r in districts
            ]
            p = _unique_csv("cip_district.csv")
            _write_csv(p, rows, ["district_id", "district_name", "state_id", "active"])
            _import_csv("cip_district", p)
        stations = lookups.get("stations") or []
        if stations:
            rows = [
                {
                    "unit_id": r["id"],
                    "unit_name": r["name"],
                    "type_id": 1,
                    "state_id": 1,
                    "district_id": r.get("district_id") or 443,
                    "active": 1,
                }
                for r in stations
            ]
            p = _unique_csv("cip_unit.csv")
            _write_csv(
                p,
                rows,
                [
                    "unit_id",
                    "unit_name",
                    "type_id",
                    "state_id",
                    "district_id",
                    "active",
                ],
            )
            _import_csv("cip_unit", p)

    if args.masters_only:
        print("DONE (masters-only).")
        return 0

    # --- cases (unless children-only) ---
    case_cols = [
        "crime_no",
        "case_no",
        "crime_registered_date",
        "police_person_id",
        "police_station_id",
        "case_category_id",
        "gravity_offence_id",
        "crime_major_head_id",
        "crime_minor_head_id",
        "case_status_id",
        "court_id",
        "incident_from_date",
        "incident_to_date",
        "info_received_ps_date",
        "latitude",
        "longitude",
        "brief_facts",
    ]
    if not args.children_only:
        case_rows = [_pick(c, case_cols) for c in cases]
        case_csv = _unique_csv("cip_case_master.csv")
        _write_csv(case_csv, case_rows, case_cols)
        _import_csv("cip_case_master", case_csv)

    # --- map crime_no → live ROWID ---
    export_path = _export_and_download("cip_case_master", OUT / "exports")
    exported = _parse_export_csv(export_path)
    print(f"live case export rows: {len(exported)}")
    crime_to_rowid: dict[str, int] = {}
    for r in exported:
        cn = r.get("crime_no") or r.get("CRIME_NO")
        rid = r.get("ROWID") or r.get("rowid")
        if cn and rid:
            crime_to_rowid[str(cn)] = int(rid)
    old_to_new_case: dict[int, int] = {}
    for c in cases:
        new_id = crime_to_rowid.get(str(c["crime_no"]))
        if new_id is None:
            print(f"WARN: no live ROWID for crime_no={c['crime_no']}")
            continue
        old_to_new_case[int(c["ROWID"])] = new_id
    print(f"mapped {len(old_to_new_case)} cases")

    def remap_children(
        table: str,
        src_key: str,
        cols: list[str],
        *,
        transform: Any = None,
    ) -> None:
        if table in skip_tables:
            print(f"skip {table}: --skip-tables")
            return
        rows_out: list[dict[str, Any]] = []
        for row in tables.get(src_key) or []:
            old = int(row.get("case_master_id") or 0)
            if old not in allowed or old not in old_to_new_case:
                continue
            payload = _pick(row, cols)
            payload["case_master_id"] = old_to_new_case[old]
            if transform:
                payload = transform(payload, row)
            rows_out.append(payload)
        if not rows_out:
            print(f"skip {table}: 0 rows")
            return
        path = _unique_csv(f"{table}.csv")
        _write_csv(path, rows_out, ["case_master_id", *cols])
        _import_csv(table, path)

    remap_children(
        "cip_victim",
        "cip_victim",
        ["victim_name", "age_year", "gender_id", "victim_police"],
    )
    remap_children(
        "cip_act_section_association",
        "cip_act_section_association",
        ["act_id", "section_id", "act_order_id", "section_order_id"],
    )

    # complainants: mock uses *_key; live table expects *_id — store nulls for ids
    comp_rows: list[dict[str, Any]] = []
    for row in tables.get("cip_complainant_details") or []:
        old = int(row.get("case_master_id") or 0)
        if old not in allowed or old not in old_to_new_case:
            continue
        comp_rows.append(
            {
                "case_master_id": old_to_new_case[old],
                "complainant_name": row.get("complainant_name"),
                "age_year": row.get("age_year"),
                "gender_id": row.get("gender_id"),
                "occupation_id": row.get("occupation_id") or "",
                "religion_id": row.get("religion_id") or "",
                "caste_id": row.get("caste_id") or "",
            }
        )
    if "cip_complainant_details" in skip_tables:
        print("skip cip_complainant_details: --skip-tables")
    elif comp_rows:
        p = _unique_csv("cip_complainant_details.csv")
        cols = [
            "case_master_id",
            "complainant_name",
            "age_year",
            "gender_id",
            "occupation_id",
            "religion_id",
            "caste_id",
        ]
        _write_csv(p, comp_rows, cols)
        _import_csv("cip_complainant_details", p)

    remap_children(
        "cip_inv_occurance_time",
        "cip_inv_occurance_time",
        [
            "occurrence_from",
            "occurrence_to",
            "place_of_occurrence",
            "beat_number",
            "distance_from_ps_km",
            "direction_from_ps",
            "village_or_city",
        ],
    )

    # accused → need old→new accused map for arrests
    accused_rows: list[dict[str, Any]] = []
    old_accused: list[dict[str, Any]] = []
    for row in tables.get("cip_accused") or []:
        old = int(row.get("case_master_id") or 0)
        if old not in allowed or old not in old_to_new_case:
            continue
        payload = {
            "case_master_id": old_to_new_case[old],
            "accused_name": row.get("accused_name"),
            "age_year": row.get("age_year"),
            "gender_id": row.get("gender_id"),
            "person_id": row.get("person_id") or "",
        }
        accused_rows.append(payload)
        old_accused.append(row)
    if "cip_accused" in skip_tables:
        print("skip cip_accused: --skip-tables (still mapping live ROWIDs for arrests)")
        old_to_new_accused = {}
    elif accused_rows:
        p = _unique_csv("cip_accused.csv")
        _write_csv(
            p,
            accused_rows,
            ["case_master_id", "accused_name", "age_year", "gender_id", "person_id"],
        )
        _import_csv("cip_accused", p)
        export_acc = _export_and_download("cip_accused", OUT / "exports")
        acc_exported = _parse_export_csv(export_acc)
        # Map by (case_master_id, person_id or accused_name)
        live_acc_index: dict[tuple[Any, Any], int] = {}
        for r in acc_exported:
            key = (
                int(r.get("case_master_id") or 0),
                str(r.get("person_id") or r.get("accused_name") or ""),
            )
            live_acc_index[key] = int(r.get("ROWID") or 0)
        old_to_new_accused = {}
        for row in old_accused:
            new_case = old_to_new_case[int(row["case_master_id"])]
            key = (new_case, str(row.get("person_id") or row.get("accused_name") or ""))
            new_acc = live_acc_index.get(key)
            if new_acc:
                old_to_new_accused[int(row["ROWID"])] = new_acc
        print(f"mapped {len(old_to_new_accused)} accused")
    else:
        old_to_new_accused = {}

    if "cip_accused" in skip_tables and accused_rows:
        export_acc = _export_and_download("cip_accused", OUT / "exports")
        acc_exported = _parse_export_csv(export_acc)
        live_acc_index = {}
        for r in acc_exported:
            key = (
                int(r.get("case_master_id") or 0),
                str(r.get("person_id") or r.get("accused_name") or ""),
            )
            live_acc_index[key] = int(r.get("ROWID") or 0)
        for row in old_accused:
            new_case = old_to_new_case[int(row["case_master_id"])]
            key = (new_case, str(row.get("person_id") or row.get("accused_name") or ""))
            new_acc = live_acc_index.get(key)
            if new_acc:
                old_to_new_accused[int(row["ROWID"])] = new_acc
        print(f"mapped {len(old_to_new_accused)} accused")

    arrest_rows: list[dict[str, Any]] = []
    for row in tables.get("cip_arrest_surrender") or []:
        old = int(row.get("case_master_id") or 0)
        if old not in allowed or old not in old_to_new_case:
            continue
        old_acc = row.get("accused_master_id")
        new_acc = ""
        if old_acc is not None and int(old_acc) in old_to_new_accused:
            new_acc = old_to_new_accused[int(old_acc)]
        arrest_rows.append(
            {
                "case_master_id": old_to_new_case[old],
                "arrest_surrender_type_id": row.get("arrest_surrender_type_id"),
                "arrest_surrender_date": row.get("arrest_surrender_date") or "",
                "arrest_surrender_state_id": row.get("arrest_surrender_state_id") or "",
                "arrest_surrender_district_id": row.get("arrest_surrender_district_id")
                or "",
                "police_station_id": row.get("police_station_id") or "",
                "io_id": row.get("io_id") or "",
                "court_id": row.get("court_id") or "",
                "accused_master_id": new_acc,
                "is_accused": row.get("is_accused", True),
                "is_complainant_accused": row.get("is_complainant_accused", False),
            }
        )
    if "cip_arrest_surrender" in skip_tables:
        print("skip cip_arrest_surrender: --skip-tables")
    elif arrest_rows:
        cols = [
            "case_master_id",
            "arrest_surrender_type_id",
            "arrest_surrender_date",
            "arrest_surrender_state_id",
            "arrest_surrender_district_id",
            "police_station_id",
            "io_id",
            "court_id",
            "accused_master_id",
            "is_accused",
            "is_complainant_accused",
        ]
        p = _unique_csv("cip_arrest_surrender.csv")
        _write_csv(p, arrest_rows, cols)
        _import_csv("cip_arrest_surrender", p)

    cs_rows: list[dict[str, Any]] = []
    for row in tables.get("cip_chargesheet_details") or []:
        old = int(row.get("case_master_id") or 0)
        if old not in allowed or old not in old_to_new_case:
            continue
        cs_rows.append(
            {
                "case_master_id": old_to_new_case[old],
                "cs_date": row.get("cs_date") or "",
                "cs_type": row.get("cs_type"),
                "police_person_id": row.get("police_person_id") or "",
            }
        )
    if "cip_chargesheet_details" in skip_tables:
        print("skip cip_chargesheet_details: --skip-tables")
    elif cs_rows:
        p = _unique_csv("cip_chargesheet_details.csv")
        _write_csv(
            p, cs_rows, ["case_master_id", "cs_date", "cs_type", "police_person_id"]
        )
        _import_csv("cip_chargesheet_details", p)

    print("DONE. Verify: curl .../api/v1/cases?limit=3")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("SEED FAILED:", type(exc).__name__, exc)
        raise SystemExit(1) from None
