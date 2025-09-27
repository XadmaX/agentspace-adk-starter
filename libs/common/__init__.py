"""Shared utilities for agentspace services."""

import importlib
from typing import Any


__all__ = [
    "github_client",
    "google_clients",
    "jira_client",
    "logging",
    "schemas",
    "testrail_client",
    "VertexLLM",
]


def __getattr__(name: str) -> Any:  # pragma: no cover - simple lazy loader
    if name == "VertexLLM":
        from .llm import VertexLLM

        return VertexLLM
    if name in {
        "github_client",
        "google_clients",
        "jira_client",
        "logging",
        "schemas",
        "testrail_client",
    }:
        return importlib.import_module(f"{__name__}.{name}")
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
