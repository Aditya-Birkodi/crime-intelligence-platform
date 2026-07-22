"""Service stub for `inv_arrestsurrenderaccused`.

TODO: Junction linking ArrestSurrender to multiple Accused.
"""

from __future__ import annotations

from app.repositories.case.inv_arrest_surrender_accused import (
    InvArrestSurrenderAccusedRepository,
)
from app.services.base import BaseService


class InvArrestSurrenderAccusedService(BaseService[object, int]):
    """Application service for `inv_arrestsurrenderaccused`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: InvArrestSurrenderAccusedRepository) -> None:
        super().__init__(repository)
