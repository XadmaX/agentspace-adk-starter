"""Client helpers for interacting with GitHub App installations."""
from __future__ import annotations

import datetime as dt
import os
from typing import Any, Dict, Optional

import jwt  # type: ignore[import-not-found]
import requests

GITHUB_API_BASE = "https://api.github.com"


class GitHubClient:
    """GitHub App REST client that exchanges installation tokens on demand."""

    def __init__(self, session: Optional[requests.Session] = None) -> None:
        self._app_id = os.getenv("GITHUB_APP_ID")
        self._private_key = os.getenv("GITHUB_PRIVATE_KEY")
        self._installation_id = os.getenv("GITHUB_INSTALLATION_ID")

        if not (self._app_id and self._private_key and self._installation_id):
            raise ValueError(
                "GITHUB_APP_ID, GITHUB_PRIVATE_KEY, and GITHUB_INSTALLATION_ID environment variables are required"
            )

        self._private_key = self._private_key.replace("\\n", "\n")
        self._session = session or requests.Session()
        self._installation_token: Optional[str] = None
        self._installation_token_expiry: Optional[dt.datetime] = None

    def _create_jwt(self) -> str:
        now = dt.datetime.utcnow()
        payload = {
            "iat": int((now - dt.timedelta(seconds=60)).timestamp()),
            "exp": int((now + dt.timedelta(minutes=10)).timestamp()),
            "iss": self._app_id,
        }
        token = jwt.encode(payload, self._private_key, algorithm="RS256")
        return token if isinstance(token, str) else token.decode("utf-8")

    def _auth_headers(self) -> Dict[str, str]:
        token = self._get_installation_token()
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
        }

    def _get_installation_token(self) -> str:
        if self._installation_token and self._installation_token_expiry:
            if self._installation_token_expiry > dt.datetime.utcnow() + dt.timedelta(minutes=1):
                return self._installation_token

        jwt_token = self._create_jwt()
        response = self._session.post(
            f"{GITHUB_API_BASE}/app/installations/{self._installation_id}/access_tokens",
            headers={
                "Authorization": f"Bearer {jwt_token}",
                "Accept": "application/vnd.github+json",
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        self._installation_token = data.get("token")
        expires_at = data.get("expires_at")
        if expires_at:
            self._installation_token_expiry = dt.datetime.fromisoformat(expires_at.replace("Z", "+00:00")).replace(
                tzinfo=None
            )
        else:
            self._installation_token_expiry = None
        if not self._installation_token:
            raise RuntimeError("GitHub installation token response did not include a token")
        return self._installation_token

    def create_issue_comment(self, owner: str, repo: str, pr_number: int, body: str) -> Dict[str, Any]:
        response = self._session.post(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues/{pr_number}/comments",
            headers=self._auth_headers(),
            json={"body": body},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    def list_files_in_pr(self, owner: str, repo: str, pr_number: int) -> Any:
        response = self._session.get(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/files",
            headers=self._auth_headers(),
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    def dispatch_workflow(
        self,
        owner: str,
        repo: str,
        workflow_file: str,
        ref: str,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> None:
        response = self._session.post(
            f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/workflows/{workflow_file}/dispatches",
            headers=self._auth_headers(),
            json={"ref": ref, "inputs": inputs or {}},
            timeout=15,
        )
        response.raise_for_status()

