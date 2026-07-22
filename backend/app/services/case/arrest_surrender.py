"""Service stub for `ArrestSurrender`.

TODO: Arrest/surrender events; FKs to State/District/Unit/Employee/Court/Accused.
"""

from __future__ import annotations

from app.repositories.case.arrest_surrender import ArrestSurrenderRepository
from app.services.base import BaseService


class ArrestSurrenderService(BaseService[object, int]):
    """Application service for `ArrestSurrender`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: ArrestSurrenderRepository) -> None:
        super().__init__(repository)
