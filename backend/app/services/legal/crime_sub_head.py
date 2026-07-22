"""Service stub for `CrimeSubHead`.

TODO: Crime sub-head under CrimeHead.
"""

from __future__ import annotations

from app.repositories.legal.crime_sub_head import CrimeSubHeadRepository
from app.services.base import BaseService


class CrimeSubHeadService(BaseService[object, int]):
    """Application service for `CrimeSubHead`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: CrimeSubHeadRepository) -> None:
        super().__init__(repository)
