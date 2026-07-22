"""Enterprise structured logging.

Separate handlers for:
  - application.log — general application events
  - api.log         — HTTP request / response metadata
  - error.log       — ERROR+ exceptions
  - ai.log          — AI / QuickML / Zia subsystem

TODO: Ship logs to Catalyst observability / centralized aggregation.
"""

from __future__ import annotations

import logging
import logging.config
from pathlib import Path

from app.core.config import get_settings

APPLICATION_LOGGER = "cip.application"
API_LOGGER = "cip.api"
ERROR_LOGGER = "cip.error"
AI_LOGGER = "cip.ai"


def setup_logging() -> None:
    """Configure dictConfig-based multi-file logging."""
    settings = get_settings()
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": (
                        "%(asctime)s | %(levelname)-8s | %(name)s | "
                        "%(filename)s:%(lineno)d | %(message)s"
                    ),
                },
                "json_like": {
                    "format": (
                        '{"ts":"%(asctime)s","level":"%(levelname)s",'
                        '"logger":"%(name)s","msg":"%(message)s"}'
                    ),
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": level,
                    "formatter": "standard",
                    "stream": "ext://sys.stdout",
                },
                "application_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": level,
                    "formatter": "standard",
                    "filename": str(log_dir / "application.log"),
                    "maxBytes": 10_485_760,
                    "backupCount": 5,
                },
                "api_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": level,
                    "formatter": "json_like",
                    "filename": str(log_dir / "api.log"),
                    "maxBytes": 10_485_760,
                    "backupCount": 5,
                },
                "error_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": logging.ERROR,
                    "formatter": "standard",
                    "filename": str(log_dir / "error.log"),
                    "maxBytes": 10_485_760,
                    "backupCount": 10,
                },
                "ai_file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": level,
                    "formatter": "json_like",
                    "filename": str(log_dir / "ai.log"),
                    "maxBytes": 10_485_760,
                    "backupCount": 5,
                },
            },
            "loggers": {
                APPLICATION_LOGGER: {
                    "handlers": ["console", "application_file", "error_file"],
                    "level": level,
                    "propagate": False,
                },
                API_LOGGER: {
                    "handlers": ["console", "api_file", "error_file"],
                    "level": level,
                    "propagate": False,
                },
                ERROR_LOGGER: {
                    "handlers": ["console", "error_file"],
                    "level": logging.ERROR,
                    "propagate": False,
                },
                AI_LOGGER: {
                    "handlers": ["console", "ai_file", "error_file"],
                    "level": level,
                    "propagate": False,
                },
            },
            "root": {
                "handlers": ["console", "application_file", "error_file"],
                "level": level,
            },
        }
    )


def get_application_logger() -> logging.Logger:
    return logging.getLogger(APPLICATION_LOGGER)


def get_api_logger() -> logging.Logger:
    return logging.getLogger(API_LOGGER)


def get_error_logger() -> logging.Logger:
    return logging.getLogger(ERROR_LOGGER)


def get_ai_logger() -> logging.Logger:
    return logging.getLogger(AI_LOGGER)
