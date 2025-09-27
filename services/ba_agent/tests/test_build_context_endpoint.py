"""Integration-style test for the /build-context endpoint."""
from __future__ import annotations

import asyncio
import json
from typing import Any, Dict
from unittest.mock import MagicMock

import sitecustomize  # noqa: F401  # Ensure compatibility patches are applied

from fastapi.routing import APIRoute

from services.ba_agent.app.context_builder import ContextBuilder
from services.ba_agent.app.main import BuildContextBody, create_app


def test_build_context_endpoint_success() -> None:
    jira_client = MagicMock()
    jira_client.get_issue.return_value = {
        "fields": {
            "summary": "Feature Y",
            "description": "Acceptance: done\nRisks: none",
        }
    }

    llm_client = MagicMock()
    llm_client.generate_json.return_value = {
        "summary": "Feature Y refined",
        "risks": ["Scope creep"],
        "acceptance": ["QA sign-off"],
    }

    firestore_client = MagicMock()
    collection = MagicMock()
    doc_ref = MagicMock()
    firestore_client.collection.return_value = collection
    collection.document.return_value = doc_ref

    publisher_client = MagicMock()
    publisher_client.topic_path.return_value = "projects/demo/topics/context.updated"
    publish_future = MagicMock()
    publisher_client.publish.return_value = publish_future

    builder = ContextBuilder(
        jira_client=jira_client,
        llm_client=llm_client,
        firestore_client=firestore_client,
        publisher_client=publisher_client,
        project_id="demo",
        topic="context.updated",
        collection="context-packs",
    )

    payload = {"issueKey": "PROJ-789", "sources": ["jira", "confluence"], "force": False}
    body = BuildContextBody.parse_obj(payload)

    app = create_app()
    route = next(r for r in app.routes if isinstance(r, APIRoute) and r.path == "/build-context")

    data: Dict[str, Any] = asyncio.run(route.endpoint(body, builder))

    assert data["issue_key"] == "PROJ-789"
    assert data["summary"] == "Feature Y refined"
    assert data["risks"] == ["Scope creep"]
    assert data["acceptance"] == ["QA sign-off"]

    jira_client.get_issue.assert_called_once_with("PROJ-789")
    doc_ref.set.assert_called_once()
    publisher_client.publish.assert_called_once()

    published_payload = json.loads(publisher_client.publish.call_args[0][1].decode("utf-8"))
    assert published_payload["force"] is False
    assert published_payload["sources"] == ["jira", "confluence"]

    publish_future.result.assert_called_once()
