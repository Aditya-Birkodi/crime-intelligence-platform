"""Service stub for `CrimeHead`.

TODO: Major crime head / crime group.
"""

from __future__ import annotations

from app.repositories.legal.crime_head import CrimeHeadRepository
from app.services.base import BaseService


class CrimeHeadService(BaseService[object, int]):
    """Application service for `CrimeHead`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: CrimeHeadRepository) -> None:
        super().__init__(repository)
