"""Minimal Jira REST client used by the agents."""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests


class JiraClient:
    def __init__(self, session: Optional[requests.Session] = None) -> None:
        base_url = os.getenv("JIRA_BASE_URL")
        username = os.getenv("JIRA_USER")
        api_token = os.getenv("JIRA_API_TOKEN")
        if not (base_url and username and api_token):
            raise ValueError("JIRA_BASE_URL, JIRA_USER, and JIRA_API_TOKEN must be set")

        self._base_url = base_url.rstrip("/")
        self._session = session or requests.Session()
        self._session.auth = (username, api_token)

    def create_or_update_issue(self, key: Optional[str], fields: Dict[str, Any]) -> Dict[str, Any]:
        if key:
            response = self._session.put(
                f"{self._base_url}/rest/api/3/issue/{key}",
                json={"fields": fields},
                timeout=15,
            )
        else:
            response = self._session.post(
                f"{self._base_url}/rest/api/3/issue",
                json={"fields": fields},
                timeout=15,
            )
        response.raise_for_status()
        return response.json()

    def add_comment(self, key: str, body: str) -> Dict[str, Any]:
        response = self._session.post(
            f"{self._base_url}/rest/api/3/issue/{key}/comment",
            json={"body": body},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

