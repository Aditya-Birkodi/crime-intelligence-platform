"""Socio-economic overlay schemas (challenge capability #3)."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class SocioEconomicIndicator(BaseModel):
    district_id: int
    district_name: str
    population_density_per_km2: float
    urbanization_pct: float
    literacy_pct: float
    youth_unemployment_pct: float
    per_capita_income_index: float
    is_urban_core: bool = False


class DistrictSocioCrimeCorrelation(BaseModel):
    district_id: int
    district_name: str
    case_count: int
    avg_latitude: Decimal | None = None
    avg_longitude: Decimal | None = None
    population_density_per_km2: float
    urbanization_pct: float
    literacy_pct: float
    youth_unemployment_pct: float
    per_capita_income_index: float
    is_urban_core: bool = False
    crime_per_10k_density: float = Field(
        description="case_count normalized by population density proxy"
    )
    correlation_note: str = ""


class SocioEconomicOverlayResponse(BaseModel):
    districts: list[DistrictSocioCrimeCorrelation]
    insight: str = ""
    provider: str = "catalyst_socio_demo"
