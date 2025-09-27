"""Configuration for the BA agent service."""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Runtime configuration loaded from the environment."""

    service_name: str = "ba-agent"
    environment: str = "local"
    project_id: str = "local-project"
    location: str = "us-central1"

    jira_base_url: str = "https://example.atlassian.net"
    jira_user: str = "bot@example.com"
    jira_api_token: str = "changeme"

    pubsub_topic_context_updated: str = "context.updated"
    firestore_embeddings_bucket: str = ""

    google_credentials_path: Optional[str] = None
    context_collection: str = "context-packs"
    pubsub_subscription_context_updated: Optional[str] = None

    class Config:
        env_prefix = ""
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
