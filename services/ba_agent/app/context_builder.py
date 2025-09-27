"""Core business logic for building a context pack."""

from __future__ import annotations

import json
import logging
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from google.cloud import pubsub_v1  # type: ignore[import-not-found]
from google.cloud.firestore_v1 import (
    Client as FirestoreClient,  # type: ignore[import-not-found]
)

from libs.common.jira_client import JiraClient
from libs.common.llm import VertexAIClient
from libs.common.schemas import ContextPack

LOGGER = logging.getLogger(__name__)


LLM_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "risks": {"type": "array", "items": {"type": "string"}},
        "acceptance": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["summary", "acceptance"],
}


@dataclass
class BuildContextRequest:
    """Normalized request payload for the build context endpoint."""

    issue_key: str
    sources: Iterable[str]
    force: bool = False


class ContextBuilder:
    """Orchestrates data collection and persistence for context packs."""

    def __init__(
        self,
        jira_client: JiraClient,
        llm_client: VertexAIClient,
        firestore_client: FirestoreClient,
        publisher_client: pubsub_v1.PublisherClient,
        project_id: str,
        topic: str,
        collection: str,
    ) -> None:
        self._jira_client = jira_client
        self._llm_client = llm_client
        self._firestore = firestore_client
        self._publisher = publisher_client
        self._project_id = project_id
        self._topic = topic
        self._collection = collection

    def build_context(self, request: BuildContextRequest) -> ContextPack:
        issue = self._jira_client.get_issue(request.issue_key)
        fields: dict[str, Any] = (
            issue.get("fields", {}) if isinstance(issue, dict) else {}
        )

        summary = self._extract_summary(fields)
        description = self._extract_description(fields)

        llm_payload = self._call_llm(description, summary)

        risks = self._ensure_list(llm_payload.get("risks"))
        acceptance = self._ensure_list(llm_payload.get("acceptance"))
        summary_from_llm = llm_payload.get("summary") or summary

        context_pack = ContextPack(
            issue_key=request.issue_key,
            summary=summary_from_llm,
            risks=risks,
            acceptance=acceptance,
        )

        self._persist_context(context_pack)
        self._publish_event(context_pack, request)

        return context_pack

    def _extract_summary(self, fields: dict[str, Any]) -> str:
        return str(fields.get("summary", ""))

    def _extract_description(self, fields: dict[str, Any]) -> str:
        description = fields.get("description")
        if isinstance(description, dict):
            # Jira's rich text format stores the content under ``content`` blocks.
            return self._flatten_jira_description(description)
        if description is None:
            return ""
        return str(description)

    def _flatten_jira_description(self, description: dict[str, Any]) -> str:
        def _collect_text(block: dict[str, Any], parts: list[str]) -> None:
            block_type = block.get("type")
            if block_type == "text":
                text = block.get("text")
                if text:
                    parts.append(str(text))
            for child in block.get("content", []) or []:
                if isinstance(child, dict):
                    _collect_text(child, parts)

        sections: list[str] = []
        for block in description.get("content", []) or []:
            if isinstance(block, dict):
                _collect_text(block, sections)
        return "\n".join(section for section in sections if section)

    def _call_llm(self, description: str, summary: str) -> dict[str, Any]:
        prompt = (
            "You are an assistant that extracts structured information from Jira descriptions.\n"
            "Given the following summary and description, return JSON matching the schema "
            "with fields summary, risks[], acceptance[].\n"
            f"Summary: {summary}\n"
            f"Description:\n{description or '(empty)'}"
        )

        response = self._llm_client.generate_json(prompt, LLM_SCHEMA)
        if not isinstance(response, dict):  # pragma: no cover - defensive
            raise ValueError("LLM response must be a dictionary")
        return response

    def _ensure_list(self, value: Any | None) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value if item]
        if value is None:
            return []
        return [str(value)]

    def _persist_context(self, context_pack: ContextPack) -> None:
        doc_ref = self._firestore.collection(self._collection).document(
            context_pack.issue_key
        )
        doc_ref.set(context_pack.dict())

    def _publish_event(
        self, context_pack: ContextPack, request: BuildContextRequest
    ) -> None:
        topic_path = self._normalise_topic(self._topic)
        event_payload = {
            "event": "context.updated",
            "issueKey": context_pack.issue_key,
            "force": request.force,
            "sources": list(request.sources),
            "context": context_pack.dict(),
        }
        data = json.dumps(event_payload).encode("utf-8")
        future = self._publisher.publish(topic_path, data)
        future.result()

    def _normalise_topic(self, topic: str) -> str:
        if topic.startswith("projects/"):
            return topic
        return self._publisher.topic_path(self._project_id, topic)


__all__ = [
    "BuildContextRequest",
    "ContextBuilder",
    "LLM_SCHEMA",
]
