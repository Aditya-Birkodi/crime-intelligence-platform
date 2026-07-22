"""Service stub for `Unit`.

TODO: Police unit / station; hierarchical ParentUnit.
"""

from __future__ import annotations

from app.repositories.geography.unit import UnitRepository
from app.services.base import BaseService


class UnitService(BaseService[object, int]):
    """Application service for `Unit`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: UnitRepository) -> None:
        super().__init__(repository)
