"""Standalone entry point for running the BA agent with Uvicorn."""

from __future__ import annotations

from services.ba_agent.app.main import app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
