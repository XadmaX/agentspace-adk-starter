"""BA agent service package."""

from .app.main import app, create_app  # noqa: F401

__all__ = ["app", "create_app"]
