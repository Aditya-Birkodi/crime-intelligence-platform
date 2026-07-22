"""FastAPI exception handlers.

TODO: Align error JSON shape with Catalyst API Gateway conventions.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging import get_error_logger
from app.exceptions.base import (
    AppException,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI app."""

    logger = get_error_logger()

    @app.exception_handler(NotFoundError)
    async def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404, content={"code": exc.code, "message": exc.message}
        )

    @app.exception_handler(ValidationError)
    async def validation_handler(
        _request: Request, exc: ValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422, content={"code": exc.code, "message": exc.message}
        )

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_handler(
        _request: Request, exc: UnauthorizedError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401, content={"code": exc.code, "message": exc.message}
        )

    @app.exception_handler(AppException)
    async def app_exception_handler(
        _request: Request, exc: AppException
    ) -> JSONResponse:
        logger.error("AppException: %s", exc.message)
        return JSONResponse(
            status_code=400, content={"code": exc.code, "message": exc.message}
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"code": "internal_error", "message": "Internal server error"},
        )
