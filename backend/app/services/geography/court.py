"""Service stub for `Court`.

TODO: Court master; District/State FKs.
"""

from __future__ import annotations

from app.repositories.geography.court import CourtRepository
from app.services.base import BaseService


class CourtService(BaseService[object, int]):
    """Application service for `Court`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: CourtRepository) -> None:
        super().__init__(repository)
