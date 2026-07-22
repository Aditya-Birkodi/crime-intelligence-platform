"""Unit tests for CrimeNo validation."""

from __future__ import annotations

import pytest

from app.utils.crime_no import build_crime_no, parse_crime_no, validate_crime_no


def test_validate_example_fir() -> None:
    assert validate_crime_no("104430006202600001") is True


def test_parse_crime_no_parts() -> None:
    parsed = parse_crime_no("104430006202600001")
    assert parsed.category_code == "1"
    assert parsed.district_id == "0443"
    assert parsed.police_station_id == "0006"
    assert parsed.year == "2026"
    assert parsed.serial == "00001"
    assert parsed.case_no_suffix == "202600001"


def test_build_crime_no() -> None:
    assert (
        build_crime_no(
            category_code="1",
            district_id=443,
            police_station_id=6,
            year=2026,
            serial=1,
        )
        == "104430006202600001"
    )


def test_invalid_length() -> None:
    assert validate_crime_no("123") is False
    with pytest.raises(ValueError):
        parse_crime_no("123")


def test_invalid_category() -> None:
    with pytest.raises(ValueError, match="category"):
        parse_crime_no("204430006202600001")
