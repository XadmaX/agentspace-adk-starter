"""Placeholder TestRail client with minimal functionality."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import requests


@dataclass
class TestRailConfig:
    base_url: str
    username: str
    api_key: str


class TestRailClient:
    def __init__(self, config: TestRailConfig) -> None:
        self._config = config
        self._session = requests.Session()
        self._session.auth = (config.username, config.api_key)

    def get_test_case(self, case_id: int) -> Dict[str, Any]:
        response = self._session.get(
            f"{self._config.base_url}/index.php?/api/v2/get_case/{case_id}", timeout=10
        )
        response.raise_for_status()
        return response.json()

    def create_test_run(self, project_id: int, suite_id: int, name: str) -> Dict[str, Any]:
        response = self._session.post(
            f"{self._config.base_url}/index.php?/api/v2/add_run/{project_id}",
            json={"suite_id": suite_id, "name": name},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

