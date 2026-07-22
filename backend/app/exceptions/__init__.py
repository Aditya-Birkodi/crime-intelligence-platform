"""Exceptions package."""

from app.exceptions.base import (
    AppException,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)

__all__ = ["AppException", "NotFoundError", "UnauthorizedError", "ValidationError"]
