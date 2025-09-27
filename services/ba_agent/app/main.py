"""Entry point for the BA agent FastAPI application."""

from __future__ import annotations

from typing import Iterable

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field

from google.cloud import pubsub_v1  # type: ignore[import-not-found]
from google.cloud.firestore_v1 import Client as FirestoreClient  # type: ignore[import-not-found]

from libs.common.google_clients import get_firestore, get_pubsub
from libs.common.jira_client import JiraClient, JiraConfig
from libs.common.llm import VertexAIClient, VertexAIConfig
from libs.common.logging import configure_json_logging

from .config import get_settings
from .context_builder import BuildContextRequest, ContextBuilder


class BuildContextBody(BaseModel):
    issue_key: str = Field(..., alias="issueKey")
    sources: Iterable[str] = Field(default_factory=list)
    force: bool = False

    class Config:
        allow_population_by_field_name = True


def get_jira_client(settings=Depends(get_settings)) -> JiraClient:
    config = JiraConfig(
        base_url=settings.jira_base_url,
        username=settings.jira_user,
        api_token=settings.jira_api_token,
    )
    return JiraClient(config)


def get_llm_client(settings=Depends(get_settings)) -> VertexAIClient:
    config = VertexAIConfig(project_id=settings.project_id, location=settings.location)
    return VertexAIClient(config)


def get_firestore_client(settings=Depends(get_settings)) -> FirestoreClient:
    return get_firestore(settings.google_credentials_path)


def get_publisher_client(settings=Depends(get_settings)) -> pubsub_v1.PublisherClient:
    return get_pubsub(settings.google_credentials_path)


def get_context_builder(
    settings=Depends(get_settings),
    jira_client: JiraClient = Depends(get_jira_client),
    llm_client: VertexAIClient = Depends(get_llm_client),
    firestore_client: FirestoreClient = Depends(get_firestore_client),
    publisher_client: pubsub_v1.PublisherClient = Depends(get_publisher_client),
) -> ContextBuilder:
    return ContextBuilder(
        jira_client=jira_client,
        llm_client=llm_client,
        firestore_client=firestore_client,
        publisher_client=publisher_client,
        project_id=settings.project_id,
        topic=settings.pubsub_topic_context_updated,
        collection=settings.context_collection,
    )


def create_app() -> FastAPI:
    settings = get_settings()
    configure_json_logging(settings.service_name)

    app = FastAPI(title="BA Agent", version="0.1.0")

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz")
    async def readyz() -> dict[str, str]:
        return {"status": "ready", "environment": settings.environment}

    @app.post("/build-context")
    async def build_context(
        body: BuildContextBody,
        builder: ContextBuilder = Depends(get_context_builder),
    ):
        request = BuildContextRequest(
            issue_key=body.issue_key,
            sources=body.sources,
            force=body.force,
        )
        context_pack = builder.build_context(request)
        return context_pack.dict()

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "services.ba_agent.app.main:app", host="0.0.0.0", port=8000, reload=True
    )
