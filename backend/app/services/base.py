"""Generic service base (DI via constructor).

TODO: Add unit-of-work / transaction boundaries.
"""

from __future__ import annotations

from typing import TypeVar

from app.repositories.base import BaseRepository

T = TypeVar("T")
ID = TypeVar("ID")


class BaseService[T, ID]:
    """Service layer accepting a repository via dependency injection."""

    def __init__(self, repository: BaseRepository[T, ID]) -> None:
        self._repository = repository

    # TODO: Add domain orchestration methods per bounded context.
