"""Pub/Sub subscriber entrypoint for the BA agent."""
from __future__ import annotations

import json
import logging
from typing import Optional

from google.cloud import pubsub_v1  # type: ignore[import-not-found]
from google.cloud.pubsub_v1.subscriber.message import Message  # type: ignore[import-not-found]

from libs.common.logging import configure_json_logging

from .config import get_settings

LOGGER = logging.getLogger(__name__)


def _subscription_from_topic(topic: str, project_id: str) -> Optional[str]:
    if not topic:
        return None
    if topic.startswith("projects/"):
        parts = topic.split("/")
        try:
            topic_id = parts[-1]
            project_index = parts.index("projects") + 1
            project_from_topic = parts[project_index]
        except (ValueError, IndexError):  # pragma: no cover - defensive
            return None
        return f"projects/{project_from_topic}/subscriptions/{topic_id}-subscriber"
    return f"projects/{project_id}/subscriptions/{topic}-subscriber"


def main() -> None:
    settings = get_settings()
    configure_json_logging(settings.service_name)

    topic = settings.pubsub_topic_context_updated
    subscription_name = (
        settings.pubsub_subscription_context_updated
        or _subscription_from_topic(topic, settings.project_id)
    )
    if not subscription_name:
        LOGGER.error("Unable to determine subscription for context.updated")
        return

    subscriber_client = pubsub_v1.SubscriberClient()

    def callback(message: Message) -> None:
        try:
            payload = json.loads(message.data.decode("utf-8"))
        except json.JSONDecodeError:
            LOGGER.warning("Received invalid JSON payload", extra={"message_id": message.message_id})
            message.ack()
            return

        LOGGER.info(
            "Context updated",
            extra={
                "issueKey": payload.get("issueKey"),
                "force": payload.get("force", False),
                "sources": payload.get("sources", []),
            },
        )

        if payload.get("force"):
            LOGGER.info(
                "Rebuilding embeddings (simulated)",
                extra={"issueKey": payload.get("issueKey")},
            )

        message.ack()

    LOGGER.info("Starting subscriber", extra={"subscription": subscription_name})
    streaming_pull_future = subscriber_client.subscribe(subscription_name, callback=callback)

    try:
        streaming_pull_future.result()
    except KeyboardInterrupt:  # pragma: no cover - manual interruption
        streaming_pull_future.cancel()
        streaming_pull_future.result()


if __name__ == "__main__":
    main()

