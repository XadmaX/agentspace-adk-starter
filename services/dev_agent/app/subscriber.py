"""Pub/Sub subscriber entrypoint for the Dev agent."""

from __future__ import annotations

import logging
from typing import Optional

from google.cloud import pubsub_v1  # type: ignore[import-not-found]
from google.cloud.pubsub_v1.subscriber.message import Message  # type: ignore[import-not-found]

from libs.common.logging import configure_json_logging

from .config import get_settings

LOGGER = logging.getLogger(__name__)


def main() -> None:
    settings = get_settings()
    configure_json_logging(settings.service_name)

    subscription_name: Optional[str] = settings.pubsub_subscription
    if not subscription_name:
        LOGGER.error(
            "No subscription configured", extra={"service": settings.service_name}
        )
        return

    subscriber_client = pubsub_v1.SubscriberClient()

    def callback(message: Message) -> None:
        LOGGER.info(
            "Received message",
            extra={
                "message_id": message.message_id,
                "data": message.data.decode("utf-8"),
            },
        )
        message.ack()

    LOGGER.info("Starting subscriber", extra={"subscription": subscription_name})
    streaming_pull_future = subscriber_client.subscribe(
        subscription_name, callback=callback
    )

    try:
        streaming_pull_future.result()
    except KeyboardInterrupt:
        streaming_pull_future.cancel()
        streaming_pull_future.result()


if __name__ == "__main__":
    main()
