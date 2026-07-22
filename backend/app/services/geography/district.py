"""Service stub for `District`.

TODO: District under State.
"""

from __future__ import annotations

from app.repositories.geography.district import DistrictRepository
from app.services.base import BaseService


class DistrictService(BaseService[object, int]):
    """Application service for `District`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: DistrictRepository) -> None:
        super().__init__(repository)
