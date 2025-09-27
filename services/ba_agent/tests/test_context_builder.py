"""Unit tests for the context builder orchestration."""

from __future__ import annotations

import json
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest

from services.ba_agent.app.context_builder import BuildContextRequest, ContextBuilder


@pytest.fixture()
def jira_issue() -> Dict[str, Any]:
    return {
        "fields": {
            "summary": "Implement feature X",
            "description": "Risks: time\nAcceptance: tests pass",
        }
    }


def _builder(
    jira_issue: Dict[str, Any],
) -> tuple[ContextBuilder, MagicMock, MagicMock, MagicMock, MagicMock]:
    jira_client = MagicMock()
    jira_client.get_issue.return_value = jira_issue

    llm_client = MagicMock()
    llm_client.generate_json.return_value = {
        "summary": "Implement feature X",
        "risks": ["Tight deadline"],
        "acceptance": ["All tests green"],
    }

    firestore_client = MagicMock()
    collection = MagicMock()
    doc_ref = MagicMock()
    firestore_client.collection.return_value = collection
    collection.document.return_value = doc_ref

    publisher_client = MagicMock()
    publisher_client.topic_path.return_value = "projects/test/topics/context.updated"
    publish_future = MagicMock()
    publisher_client.publish.return_value = publish_future

    builder = ContextBuilder(
        jira_client=jira_client,
        llm_client=llm_client,
        firestore_client=firestore_client,
        publisher_client=publisher_client,
        project_id="test",
        topic="context.updated",
        collection="context-packs",
    )

    return builder, firestore_client, doc_ref, publisher_client, publish_future


def test_build_context_persists_and_publishes(jira_issue: Dict[str, Any]) -> None:
    builder, firestore_client, doc_ref, publisher_client, publish_future = _builder(
        jira_issue
    )

    request = BuildContextRequest(issue_key="PROJ-123", sources=["jira"], force=True)
    context_pack = builder.build_context(request)

    assert context_pack.summary == "Implement feature X"
    assert context_pack.risks == ["Tight deadline"]
    assert context_pack.acceptance == ["All tests green"]

    firestore_client.collection.assert_called_once_with("context-packs")
    doc_ref.set.assert_called_once_with(context_pack.dict())

    publisher_client.topic_path.assert_called_once_with("test", "context.updated")
    publisher_client.publish.assert_called_once()

    publish_future.result.assert_called_once()

    published_payload = json.loads(
        publisher_client.publish.call_args[0][1].decode("utf-8")
    )
    assert published_payload["issueKey"] == "PROJ-123"
    assert published_payload["force"] is True
    assert published_payload["event"] == "context.updated"
