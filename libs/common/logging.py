"""Utilities for consistent structured logging across services."""
from __future__ import annotations

import json
import logging
import logging.config
import socket
from datetime import UTC, datetime
from typing import Any


class JsonLogFormatter(logging.Formatter):
    """Format log records as JSON strings."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        log: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, UTC)
            .isoformat()
            .replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "hostname": socket.gethostname(),
        }

        if record.exc_info:
            log["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            log["stack"] = record.stack_info
        extra = getattr(record, "extra", None)  # type: ignore[attr-defined]
        if extra:
            log.update(extra)

        return json.dumps(log, default=str)


def configure_json_logging(service_name: str) -> None:
    """Configure root logging with JSON output suitable for uvicorn."""

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JsonLogFormatter,
            }
        },
        "handlers": {
            "default": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "json",
            }
        },
        "loggers": {
            "": {"handlers": ["default"], "level": "INFO"},
            "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "uvicorn.access": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(logging_config)
    logging.getLogger("uvicorn").info("Logging configured", extra={"service": service_name})

