"""Service stub for `Accused`.

TODO: Accused persons for a CaseMaster (1:N); PersonID sorting A1/A2/….
"""

from __future__ import annotations

from app.repositories.case.accused import AccusedRepository
from app.services.base import BaseService


class AccusedService(BaseService[object, int]):
    """Application service for `Accused`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: AccusedRepository) -> None:
        super().__init__(repository)
