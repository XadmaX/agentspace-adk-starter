"""Client helpers for interacting with GitHub App installations."""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import jwt  # type: ignore[import-not-found]
import requests

LOGGER = logging.getLogger(__name__)


@dataclass
class GitHubAppConfig:
    app_id: str
    private_key: str
    base_url: str = "https://api.github.com"


class GitHubAppClient:
    """Minimal GitHub App REST client."""

    def __init__(self, config: GitHubAppConfig) -> None:
        self._config = config
        self._session = requests.Session()

    def _create_jwt(self) -> str:
        now = int(time.time())
        payload = {
            "iat": now - 60,
            "exp": now + (10 * 60),
            "iss": self._config.app_id,
        }
        token = jwt.encode(payload, self._config.private_key, algorithm="RS256")
        return token if isinstance(token, str) else token.decode("utf-8")

    def _headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {"Accept": "application/vnd.github+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def get_installations(self) -> Dict[str, Any]:
        jwt_token = self._create_jwt()
        response = self._session.get(
            f"{self._config.base_url}/app/installations",
            headers=self._headers(jwt_token),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def create_installation_token(self, installation_id: int) -> Dict[str, Any]:
        jwt_token = self._create_jwt()
        response = self._session.post(
            f"{self._config.base_url}/app/installations/{installation_id}/access_tokens",
            headers=self._headers(jwt_token),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def get_pull_request(self, repo: str, pr_number: int, token: str) -> Dict[str, Any]:
        response = self._session.get(
            f"{self._config.base_url}/repos/{repo}/pulls/{pr_number}",
            headers=self._headers(f"token {token}"),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

