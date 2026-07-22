"""Application exception hierarchy.

TODO: Map domain errors to HTTP status codes and Catalyst API Gateway error envelopes.
"""

from __future__ import annotations


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, *, code: str = "app_error") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(AppException):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, code="not_found")


class ValidationError(AppException):
    """Domain validation failure."""

    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message, code="validation_error")


class UnauthorizedError(AppException):
    """Authentication / authorization failure."""

    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message, code="unauthorized")
