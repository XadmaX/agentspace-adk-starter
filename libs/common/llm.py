"""Vertex AI Gemini wrapper."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class VertexAIConfig:
    project_id: str
    location: str = "us-central1"
    model_name: str = "gemini-1.0-pro"
    json_model_name: str = "gemini-1.0-pro"  # Placeholder for JSON responses


class VertexAIClient:
    def __init__(self, config: VertexAIConfig) -> None:
        self._config = config
        self._client = None

    def _get_client(self):
        if self._client is None:
            from vertexai import init  # type: ignore[import-not-found]
            from vertexai.generative_models import GenerativeModel  # type: ignore[import-not-found]

            init(project=self._config.project_id, location=self._config.location)
            self._client = GenerativeModel(self._config.model_name)
        return self._client

    def text(self, prompt: str, **kwargs: Any) -> str:
        client = self._get_client()
        response = client.generate_content(prompt, **kwargs)
        return getattr(response, "text", str(response))

    def json(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        client = self._get_client()
        response = client.generate_content(prompt, **kwargs)
        if hasattr(response, "text"):
            return {"text": response.text}
        if isinstance(response, dict):
            return response
        return {"response": str(response)}

