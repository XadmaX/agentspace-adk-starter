"""Vertex AI Gemini client with retry handling."""

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


import json
import os
import time
from typing import Any, Dict, Optional

from google.api_core import exceptions as google_exceptions  # type: ignore[import-not-found]
from google.cloud import aiplatform  # type: ignore[import-not-found]
from vertexai import generative_models  # type: ignore[import-not-found]


class VertexLLM:
    """Convenience wrapper around the Vertex AI Gemini models."""

    def __init__(
        self,
        model: str = "gemini-1.5-pro",
        *,
        project: Optional[str] = None,
        location: Optional[str] = None,
        timeout: float = 60.0,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ) -> None:
        self._model_name = model
        self._project = (
            project or os.getenv("PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT")
        )
        self._location = (
            location
            or os.getenv("LOCATION")
            or os.getenv("GOOGLE_CLOUD_LOCATION")
            or "us-central1"
        )
        if not self._project:
            raise ValueError(
                "VertexLLM requires PROJECT_ID or GOOGLE_CLOUD_PROJECT to be set"
            )

        self._timeout = timeout
        self._max_retries = max(1, max_retries)
        self._retry_delay = max(0.0, retry_delay)

        aiplatform.init(project=self._project, location=self._location)
        self._model = generative_models.GenerativeModel(self._model_name)

    def generate_text(
        self,
        prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        """Generate a text response for a given prompt."""

        config = generative_models.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        response = self._invoke_with_retry(prompt, config)
        return self._extract_text(response)

    def generate_json(
        self,
        schema: Dict[str, Any],
        prompt: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """Generate a JSON response conforming to the provided schema."""

        config = generative_models.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            response_mime_type="application/json",
            response_schema=schema,
        )
        response = self._invoke_with_retry(prompt, config)

        if isinstance(response, dict):
            text_value = response.get("text")
            if isinstance(text_value, str):
                try:
                    return json.loads(text_value)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        "Vertex response did not contain valid JSON"
                    ) from exc
            return response

        text_attr = getattr(response, "text", None)
        if isinstance(text_attr, str):
            try:
                return json.loads(text_attr)
            except json.JSONDecodeError as exc:
                raise ValueError("Vertex response did not contain valid JSON") from exc

        text = self._extract_text(response)
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError("Vertex response did not contain valid JSON") from exc

    def _invoke_with_retry(
        self,
        prompt: str,
        generation_config: generative_models.GenerationConfig,
    ) -> Any:
        last_exc: Optional[Exception] = None
        for attempt in range(1, self._max_retries + 1):
            try:
                return self._model.generate_content(
                    [prompt],
                    generation_config=generation_config,
                    timeout=self._timeout,
                )
            except (
                google_exceptions.DeadlineExceeded,
                google_exceptions.ResourceExhausted,
                google_exceptions.ServiceUnavailable,
                google_exceptions.InternalServerError,
                google_exceptions.GoogleAPICallError,
            ) as exc:
                last_exc = exc
                if attempt == self._max_retries:
                    raise
                time.sleep(self._retry_delay * attempt)
        if last_exc is not None:
            raise last_exc
        raise RuntimeError("VertexLLM failed without raising an exception")

    @staticmethod
    def _extract_text(response: Any) -> str:
        if response is None:
            return ""
        text = getattr(response, "text", None)
        if text:
            return text
        candidates = getattr(response, "candidates", None)
        if candidates:
            for candidate in candidates:
                content = getattr(candidate, "content", None)
                if content:
                    parts = getattr(content, "parts", None)
                    if parts:
                        for part in parts:
                            part_text = getattr(part, "text", None)
                            if part_text:
                                return part_text
        return str(response)
