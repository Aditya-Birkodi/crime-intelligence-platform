"""Service stub for `Section`.

TODO: Section under an Act; FK ActCode.
"""

from __future__ import annotations

from app.repositories.legal.section import SectionRepository
from app.services.base import BaseService


class SectionService(BaseService[object, int]):
    """Application service for `Section`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: SectionRepository) -> None:
        super().__init__(repository)
