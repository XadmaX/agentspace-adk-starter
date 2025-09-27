"""Entry point for the Dev agent FastAPI application."""
from __future__ import annotations

from fastapi import FastAPI

from libs.common.logging import configure_json_logging

from .config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    configure_json_logging(settings.service_name)

    app = FastAPI(title="Dev Agent", version="0.1.0")

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz")
    async def readyz() -> dict[str, str]:
        return {"status": "ready", "environment": settings.environment}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("services.dev_agent.app.main:app", host="0.0.0.0", port=8001, reload=True)

