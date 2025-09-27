"""Google Cloud client helpers."""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from google.cloud import firestore, pubsub_v1  # type: ignore[import-not-found]
from google.cloud import secretmanager  # type: ignore[import-not-found]
from google.oauth2 import service_account  # type: ignore[import-not-found]


def _load_credentials(credentials_path: Optional[str]):
    if credentials_path:
        return service_account.Credentials.from_service_account_file(credentials_path)
    return None


@lru_cache(maxsize=1)
def get_pubsub(credentials_path: Optional[str] = None) -> pubsub_v1.PublisherClient:
    """Return a cached Pub/Sub publisher client."""

    credentials = _load_credentials(credentials_path)
    return pubsub_v1.PublisherClient(credentials=credentials)


@lru_cache(maxsize=1)
def get_firestore(credentials_path: Optional[str] = None) -> firestore.Client:
    """Return a cached Firestore client."""

    credentials = _load_credentials(credentials_path)
    return firestore.Client(credentials=credentials)


@lru_cache(maxsize=1)
def get_secret_manager(credentials_path: Optional[str] = None) -> secretmanager.SecretManagerServiceClient:
    """Return a cached Secret Manager client."""

    credentials = _load_credentials(credentials_path)
    return secretmanager.SecretManagerServiceClient(credentials=credentials)


def get_secret(secret_name: str, project_id: str, credentials_path: Optional[str] = None) -> str:
    """Fetch the latest secret payload as a string."""

    client = get_secret_manager(credentials_path)
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("utf-8")

