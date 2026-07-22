"""Service stub for `Designation`.

TODO: Designation (IO, SHO, …).
"""

from __future__ import annotations

from app.repositories.personnel.designation import DesignationRepository
from app.services.base import BaseService


class DesignationService(BaseService[object, int]):
    """Application service for `Designation`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: DesignationRepository) -> None:
        super().__init__(repository)
