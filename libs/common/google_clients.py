"""Helpers for constructing Google Cloud clients used across services."""
from __future__ import annotations

import json
import logging
import os
from functools import cache

from google.cloud import (  # type: ignore[import-not-found]
    firestore,
    pubsub_v1,
    secretmanager,  # type: ignore[import-not-found]
)

try:  # pragma: no cover - exercised indirectly by tests
    from pythonjsonlogger import jsonlogger
except ModuleNotFoundError:  # pragma: no cover - fallback for offline environments
    class _FallbackJsonFormatter(logging.Formatter):
        """Minimal JSON formatter when python-json-logger is unavailable."""

        def format(self, record: logging.LogRecord) -> str:
            message = {
                "level": record.levelname,
                "name": record.name,
                "message": record.getMessage(),
            }
            if record.exc_info:
                message["exc_info"] = self.formatException(record.exc_info)
            return json.dumps(message)

    class jsonlogger:  # type: ignore[override]
        JsonFormatter = _FallbackJsonFormatter


def _log_level() -> int:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    return getattr(logging, level_name, logging.INFO)


@cache
def get_logger(name: str | None = None) -> logging.Logger:
    """Return a JSON-formatted logger with level configured from the environment."""

    logger = logging.getLogger(name if name else "agentspace")
    logger.setLevel(_log_level())

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter()
        handler.setFormatter(formatter)
        handler.setLevel(_log_level())
        logger.addHandler(handler)
        logger.propagate = False

    return logger


@cache
def get_pubsub() -> pubsub_v1.PublisherClient:
    """Return a cached Pub/Sub publisher client using default credentials."""

    return pubsub_v1.PublisherClient()


@cache
def get_firestore() -> firestore.Client:
    """Return a cached Firestore client using application default credentials."""

    return firestore.Client()


@cache
def _secret_manager_client() -> secretmanager.SecretManagerServiceClient:
    return secretmanager.SecretManagerServiceClient()


def get_secret(name: str) -> str:
    """Fetch the latest payload for the given Secret Manager secret.

    Args:
        name: Secret identifier. Either a full resource name or bare secret ID.

    Returns:
        The decoded secret payload as a UTF-8 string.

    Raises:
        ValueError: If no project ID can be resolved for a bare secret name.
    """

    if name.startswith("projects/"):
        resource_name = name
    else:
        project_id = (
            os.getenv("GOOGLE_CLOUD_PROJECT")
            or os.getenv("PROJECT_ID")
            or os.getenv("GCP_PROJECT")
        )
        if not project_id:
            raise ValueError(
                "GOOGLE_CLOUD_PROJECT/PROJECT_ID environment variable is required to access secrets"
            )
        resource_name = f"projects/{project_id}/secrets/{name}/versions/latest"

    client = _secret_manager_client()
    response = client.access_secret_version(name=resource_name)
    return response.payload.data.decode("utf-8")

