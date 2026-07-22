"""Service stub for `UnitType`.

TODO: Unit type (Police Station, Circle Office, …).
"""

from __future__ import annotations

from app.repositories.geography.unit_type import UnitTypeRepository
from app.services.base import BaseService


class UnitTypeService(BaseService[object, int]):
    """Application service for `UnitType`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: UnitTypeRepository) -> None:
        super().__init__(repository)
