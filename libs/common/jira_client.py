"""Lightweight Jira client placeholder."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import requests


@dataclass
class JiraConfig:
    base_url: str
    username: str
    api_token: str


class JiraClient:
    def __init__(self, config: JiraConfig) -> None:
        self._config = config
        self._session = requests.Session()
        self._session.auth = (config.username, config.api_token)

    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        response = self._session.get(
            f"{self._config.base_url}/rest/api/3/issue/{issue_key}", timeout=10
        )
        response.raise_for_status()
        return response.json()

    def add_comment(self, issue_key: str, body: str) -> Dict[str, Any]:
        response = self._session.post(
            f"{self._config.base_url}/rest/api/3/issue/{issue_key}/comment",
            json={"body": body},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

