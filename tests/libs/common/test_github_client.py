import datetime as dt

import pytest

from libs.common.github_client import GitHubClient, GITHUB_API_BASE


class FakeResponse:
    def __init__(self, json_data=None, status_code=200):
        self._json = json_data or {}
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self):
        self.calls = []
        self._responses = {}

    def register(self, method, url, response):
        self._responses[(method, url)] = response

    def post(self, url, **kwargs):
        self.calls.append(("POST", url, kwargs))
        return self._responses[("POST", url)]

    def get(self, url, **kwargs):
        self.calls.append(("GET", url, kwargs))
        return self._responses[("GET", url)]


@pytest.fixture(autouse=True)
def github_env(monkeypatch):
    monkeypatch.setenv("GITHUB_APP_ID", "1234")
    monkeypatch.setenv("GITHUB_PRIVATE_KEY", "dummy-key")
    monkeypatch.setenv("GITHUB_INSTALLATION_ID", "9999")


@pytest.fixture
def fake_jwt(monkeypatch):
    def _encode(payload, key, algorithm):  # noqa: D401
        return "signed-jwt"

    monkeypatch.setattr("libs.common.github_client.jwt.encode", _encode)


def test_create_issue_comment_uses_installation_token(fake_jwt):
    session = FakeSession()
    expires = (dt.datetime.utcnow() + dt.timedelta(hours=1)).isoformat() + "Z"
    session.register(
        "POST",
        f"{GITHUB_API_BASE}/app/installations/9999/access_tokens",
        FakeResponse({"token": "install-token", "expires_at": expires}),
    )
    session.register(
        "POST",
        f"{GITHUB_API_BASE}/repos/octo/demo/issues/5/comments",
        FakeResponse({"id": 101, "body": "hello"}),
    )

    client = GitHubClient(session=session)
    response = client.create_issue_comment("octo", "demo", 5, "hello")

    assert response == {"id": 101, "body": "hello"}
    assert len(session.calls) == 2
    _, _, install_kwargs = session.calls[0]
    assert install_kwargs["headers"]["Authorization"] == "Bearer signed-jwt"
    _, _, comment_kwargs = session.calls[1]
    assert comment_kwargs["headers"]["Authorization"] == "Bearer install-token"
    assert comment_kwargs["json"] == {"body": "hello"}


def test_list_files_reuses_token(fake_jwt):
    session = FakeSession()
    expires = (dt.datetime.utcnow() + dt.timedelta(hours=1)).isoformat() + "Z"
    session.register(
        "POST",
        f"{GITHUB_API_BASE}/app/installations/9999/access_tokens",
        FakeResponse({"token": "install-token", "expires_at": expires}),
    )
    session.register(
        "GET",
        f"{GITHUB_API_BASE}/repos/octo/demo/pulls/42/files",
        FakeResponse(
            [
                {"filename": "app.py"},
                {"filename": "README.md"},
            ]
        ),
    )

    client = GitHubClient(session=session)
    files = client.list_files_in_pr("octo", "demo", 42)

    assert files == [{"filename": "app.py"}, {"filename": "README.md"}]
    assert len(session.calls) == 2
    _, _, file_kwargs = session.calls[1]
    assert file_kwargs["headers"]["Authorization"] == "Bearer install-token"
