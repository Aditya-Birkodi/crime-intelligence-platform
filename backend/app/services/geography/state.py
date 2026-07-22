"""Service stub for `State`.

TODO: State master; referenced by District, Unit, Court, ArrestSurrender.
"""

from __future__ import annotations

from app.repositories.geography.state import StateRepository
from app.services.base import BaseService


class StateService(BaseService[object, int]):
    """Application service for `State`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: StateRepository) -> None:
        super().__init__(repository)
