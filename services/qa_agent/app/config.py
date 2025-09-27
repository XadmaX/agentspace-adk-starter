"""Configuration for the QA agent service."""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    service_name: str = "qa-agent"
    environment: str = "local"
    google_project_id: str = "local-project"
    google_credentials_path: Optional[str] = None
    pubsub_subscription: Optional[str] = None

    class Config:
        env_prefix = "QA_AGENT_"
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

