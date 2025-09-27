import asyncio
import sitecustomize  # noqa: F401  # Ensure compatibility patches are applied

from fastapi.routing import APIRoute

from services.ba_agent.app.main import create_app


def _call_route(path: str):
    app = create_app()
    route = next(r for r in app.routes if isinstance(r, APIRoute) and r.path == path)
    return asyncio.run(route.endpoint())


def test_healthz() -> None:
    result = _call_route("/healthz")
    assert result["status"] == "ok"


def test_readyz() -> None:
    result = _call_route("/readyz")
    assert result["status"] == "ready"
