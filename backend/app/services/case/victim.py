"""Service stub for `Victim`.

TODO: Victim records for a CaseMaster (1:N).
"""

from __future__ import annotations

from app.repositories.case.victim import VictimRepository
from app.services.base import BaseService


class VictimService(BaseService[object, int]):
    """Application service for `Victim`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: VictimRepository) -> None:
        super().__init__(repository)
