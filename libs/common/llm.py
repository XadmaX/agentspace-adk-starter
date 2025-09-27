"""Vertex AI Gemini wrapper."""
from __future__ import annotations

from dataclasses import dataclass
import json
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

    def generate_json(self, prompt: str, schema: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Generate a JSON object that follows the provided ``schema``.

        This helper works with the lightweight ``json`` method above and
        normalises the return value to a dictionary.  In production we would
        pass ``schema`` to the Vertex AI client to enforce the structure, but
        for tests and local development we simply make sure that whatever the
        model returned can be parsed as JSON.
        """

        # ``schema`` is not used directly in this placeholder implementation
        # but keeping it in the signature allows the function to be mocked in
        # tests and swapped out with a stricter implementation later.
        _ = schema

        raw_response = self.json(prompt, **kwargs)
        if isinstance(raw_response, dict):
            if "text" in raw_response:
                try:
                    return json.loads(raw_response["text"])
                except json.JSONDecodeError as exc:  # pragma: no cover - defensive
                    raise ValueError("LLM response was not valid JSON") from exc
            return raw_response

        if isinstance(raw_response, str):
            try:
                return json.loads(raw_response)
            except json.JSONDecodeError as exc:  # pragma: no cover - defensive
                raise ValueError("LLM response was not valid JSON") from exc

        raise ValueError("LLM response was not a JSON compatible structure")

