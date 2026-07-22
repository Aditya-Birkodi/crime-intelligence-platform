"""Service stub for `Rank`.

TODO: Police rank hierarchy.
"""

from __future__ import annotations

from app.repositories.personnel.rank import RankRepository
from app.services.base import BaseService


class RankService(BaseService[object, int]):
    """Application service for `Rank`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: RankRepository) -> None:
        super().__init__(repository)
