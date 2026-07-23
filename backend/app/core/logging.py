"""Enterprise structured logging.

Separate handlers for:
  - application.log — general application events
  - api.log         — HTTP request / response metadata
  - error.log       — ERROR+ exceptions
  - ai.log          — AI / QuickML / Zia subsystem

On AppSail (X_ZOHO_CATALYST_LISTEN_PORT set), use console-only logging so
startup stays under the ~10s listen window and read-only FS does not crash boot.
"""

from __future__ import annotations

import logging
import logging.config
import os
from pathlib import Path
from typing import Any

from app.core.config import get_settings

APPLICATION_LOGGER = "cip.application"
API_LOGGER = "cip.api"
ERROR_LOGGER = "cip.error"
AI_LOGGER = "cip.ai"


def _on_appsail() -> bool:
    return bool(os.getenv("X_ZOHO_CATALYST_LISTEN_PORT"))


def setup_logging() -> None:
    """Configure dictConfig-based logging (files locally, console on AppSail)."""
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    console_only = _on_appsail()

    handlers: dict[str, dict[str, Any]] = {
        "console": {
            "class": "logging.StreamHandler",
            "level": level,
            "formatter": "standard",
            "stream": "ext://sys.stdout",
        },
    }
    app_handlers = ["console"]
    api_handlers = ["console"]
    error_handlers = ["console"]
    ai_handlers = ["console"]
    root_handlers = ["console"]

    if not console_only:
        log_dir = Path(settings.log_dir)
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            handlers.update(
                {
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
                }
            )
            app_handlers = ["console", "application_file", "error_file"]
            api_handlers = ["console", "api_file", "error_file"]
            error_handlers = ["console", "error_file"]
            ai_handlers = ["console", "ai_file", "error_file"]
            root_handlers = ["console", "application_file", "error_file"]
        except OSError:
            # Fall back to console if log dir is not writable
            pass

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
            "handlers": handlers,
            "loggers": {
                APPLICATION_LOGGER: {
                    "handlers": app_handlers,
                    "level": level,
                    "propagate": False,
                },
                API_LOGGER: {
                    "handlers": api_handlers,
                    "level": level,
                    "propagate": False,
                },
                ERROR_LOGGER: {
                    "handlers": error_handlers,
                    "level": logging.ERROR,
                    "propagate": False,
                },
                AI_LOGGER: {
                    "handlers": ai_handlers,
                    "level": level,
                    "propagate": False,
                },
            },
            "root": {
                "handlers": root_handlers,
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
