"""Generic repository ABC.

TODO: Implement Catalyst Data Store adapter for production.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar("T")
ID = TypeVar("ID")


class BaseRepository[T, ID](ABC):
    """Abstract repository — persistence boundary."""

    @abstractmethod
    def get_by_id(self, entity_id: ID) -> T | None:
        """Fetch entity by primary key."""

    @abstractmethod
    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[T]:
        """List entities with pagination."""

    @abstractmethod
    def add(self, entity: T) -> T:
        """Persist a new entity."""

    @abstractmethod
    def update(self, entity: T) -> T:
        """Update an existing entity."""

    @abstractmethod
    def delete(self, entity_id: ID) -> None:
        """Soft/hard delete by id."""
