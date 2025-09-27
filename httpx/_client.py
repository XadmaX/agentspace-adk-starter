"""Stubs for pieces of `httpx._client` used by Starlette's TestClient."""

from __future__ import annotations


class UseClientDefault:
    """Sentinel object used in the real httpx API."""

    pass


USE_CLIENT_DEFAULT = UseClientDefault()


__all__ = ["UseClientDefault", "USE_CLIENT_DEFAULT"]
