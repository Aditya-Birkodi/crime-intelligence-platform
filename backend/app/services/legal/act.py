"""Service stub for `Act`.

TODO: Legal act master (e.g. IPC, NDPS); PK ActCode.
"""

from __future__ import annotations

from app.repositories.legal.act import ActRepository
from app.services.base import BaseService


class ActService(BaseService[object, int]):
    """Application service for `Act`.

    TODO: Orchestrate repository calls and domain rules (no API logic here).
    """

    def __init__(self, repository: ActRepository) -> None:
        super().__init__(repository)
