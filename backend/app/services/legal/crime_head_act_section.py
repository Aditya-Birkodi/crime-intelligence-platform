"""Service stub for `CrimeHeadActSection`.

TODO: Maps CrimeHead to Act+Section combinations.
"""

from __future__ import annotations

from app.repositories.legal.crime_head_act_section import CrimeHeadActSectionRepository
from app.services.base import BaseService


class CrimeHeadActSectionService(BaseService[object, int]):
    """Application service for `CrimeHeadActSection`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: CrimeHeadActSectionRepository) -> None:
        super().__init__(repository)
