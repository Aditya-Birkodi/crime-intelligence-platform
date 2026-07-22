"""CrimeNo / CaseNo helpers per Police_FIR_ER_Diagram.pdf.

Format (18 digits):
  1 digit Case Category + 4 digit District ID + 4 digit Police Station ID
  + 4 digit Year + 5 digit Running Serial
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.core.constants import (
    CASE_CATEGORY_FIR,
    CASE_CATEGORY_PAR,
    CASE_CATEGORY_UDR,
    CASE_CATEGORY_ZERO_FIR,
    CRIME_NO_TOTAL_LENGTH,
)

_CRIME_NO_RE = re.compile(r"^\d{18}$")
_VALID_CATEGORIES = {
    CASE_CATEGORY_FIR,
    CASE_CATEGORY_UDR,
    CASE_CATEGORY_PAR,
    CASE_CATEGORY_ZERO_FIR,
}


@dataclass(frozen=True, slots=True)
class ParsedCrimeNo:
    category_code: str
    district_id: str
    police_station_id: str
    year: str
    serial: str

    @property
    def case_no_suffix(self) -> str:
        """CaseNo = YYYY + 5-digit serial (last 9 digits of CrimeNo)."""
        return f"{self.year}{self.serial}"


def validate_crime_no(crime_no: str) -> bool:
    """Return True if CrimeNo matches structural rules."""
    try:
        parse_crime_no(crime_no)
        return True
    except ValueError:
        return False


def parse_crime_no(crime_no: str) -> ParsedCrimeNo:
    """Parse and validate an 18-digit CrimeNo."""
    value = (crime_no or "").strip()
    if not _CRIME_NO_RE.match(value):
        raise ValueError(f"CrimeNo must be exactly {CRIME_NO_TOTAL_LENGTH} digits")
    category = value[0]
    if category not in _VALID_CATEGORIES:
        raise ValueError(f"Invalid case category code: {category}")
    year = value[9:13]
    if not (2000 <= int(year) <= 2100):
        raise ValueError(f"Unrealistic year in CrimeNo: {year}")
    return ParsedCrimeNo(
        category_code=category,
        district_id=value[1:5],
        police_station_id=value[5:9],
        year=year,
        serial=value[13:18],
    )


def build_crime_no(
    *,
    category_code: str,
    district_id: int,
    police_station_id: int,
    year: int,
    serial: int,
) -> str:
    """Assemble a CrimeNo from parts (zero-padded)."""
    parts = (
        str(category_code)[0],
        f"{int(district_id):04d}",
        f"{int(police_station_id):04d}",
        f"{int(year):04d}",
        f"{int(serial):05d}",
    )
    crime_no = "".join(parts)
    parse_crime_no(crime_no)
    return crime_no
