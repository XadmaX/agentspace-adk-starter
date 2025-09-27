"""TestRail client stubs used for integration points."""

from __future__ import annotations

import os
from typing import Any, Dict, List


class TestRailClient:
    def __init__(self) -> None:
        base_url = os.getenv("TESTRAIL_BASE_URL")
        username = os.getenv("TESTRAIL_USER")
        api_key = os.getenv("TESTRAIL_API_KEY")
        if not (base_url and username and api_key):
            raise ValueError(
                "TESTRAIL_BASE_URL, TESTRAIL_USER, and TESTRAIL_API_KEY must be set"
            )

        self._base_url = base_url.rstrip("/")
        self._username = username
        self._api_key = api_key

    def create_cases(
        self, project_id: int, section_id: int, cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        return {
            "project_id": project_id,
            "section_id": section_id,
            "created": cases,
        }

    def create_run(
        self, project_id: int, name: str, case_ids: List[int]
    ) -> Dict[str, Any]:
        return {
            "project_id": project_id,
            "name": name,
            "case_ids": case_ids,
        }

    def add_results(self, run_id: int, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "run_id": run_id,
            "results": results,
        }
