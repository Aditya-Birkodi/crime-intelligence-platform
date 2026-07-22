"""Middleware package.

TODO: Add Catalyst Authentication middleware and rate limiting.
"""

from app.middleware.request_logging import RequestLoggingMiddleware

__all__ = ["RequestLoggingMiddleware"]
