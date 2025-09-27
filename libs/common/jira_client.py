"""Minimal Jira REST client used by the agents."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class JiraConfig:
    """Configuration required to interact with the Jira API."""

    base_url: str
    username: str
    api_token: str

    @classmethod
    def from_env(cls) -> JiraConfig:
        base_url = os.getenv("JIRA_BASE_URL")
        username = os.getenv("JIRA_USER")
        api_token = os.getenv("JIRA_API_TOKEN")
        if not (base_url and username and api_token):
            raise ValueError("JIRA_BASE_URL, JIRA_USER, and JIRA_API_TOKEN must be set")
        return cls(base_url=base_url, username=username, api_token=api_token)


class JiraClient:
    """Very small wrapper around the Jira REST API."""

    def __init__(
        self,
        config: JiraConfig | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self._config = config or JiraConfig.from_env()
        self._base_url = self._config.base_url.rstrip("/")
        self._session = session or requests.Session()
        self._session.auth = (self._config.username, self._config.api_token)
        self._session.headers.setdefault("Accept", "application/json")

    def _build_url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def get_issue(self, key: str) -> dict[str, Any]:
        response = self._session.get(
            self._build_url(f"/rest/api/3/issue/{key}"),
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    def create_or_update_issue(
        self, key: str | None, fields: dict[str, Any]
    ) -> dict[str, Any]:
        if key:
            url = self._build_url(f"/rest/api/3/issue/{key}")
            response = self._session.put(url, json={"fields": fields}, timeout=15)
        else:
            url = self._build_url("/rest/api/3/issue")
            response = self._session.post(url, json={"fields": fields}, timeout=15)
        response.raise_for_status()
        return response.json()

    def add_comment(self, key: str, body: str) -> dict[str, Any]:
        response = self._session.post(
            self._build_url(f"/rest/api/3/issue/{key}/comment"),
            json={"body": body},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()


__all__ = ["JiraClient", "JiraConfig"]
