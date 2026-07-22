"""Service stub for `GravityOffence`.

TODO: Offence gravity (Heinous / Non-Heinous).
"""

from __future__ import annotations

from app.repositories.lookups.gravity_offence import GravityOffenceRepository
from app.services.base import BaseService


class GravityOffenceService(BaseService[object, int]):
    """Application service for `GravityOffence`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: GravityOffenceRepository) -> None:
        super().__init__(repository)
