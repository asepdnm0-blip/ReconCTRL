"""Redis Pub/Sub helpers for SSE scan events."""

from __future__ import annotations

import json
import logging
from typing import Any

import redis

from app.config import settings

logger = logging.getLogger(__name__)

_redis = redis.from_url(settings.REDIS_URL, decode_responses=True)


def publish_event(scan_id: str, event: str, data: dict[str, Any] | None = None) -> None:
    channel = f"scan:{scan_id}:events"
    payload = {"event": event, "scan_id": scan_id, **(data or {})}
    _redis.publish(channel, json.dumps(payload))
    logger.info("Published %s on %s", event, channel)


def publish_module_start(scan_id: str, module: str, message: str | None = None) -> None:
    publish_event(
        scan_id,
        "module_start",
        {"module": module, "message": message or f"Starting {module}"},
    )


def publish_module_progress(scan_id: str, module: str, progress: int, **extra: Any) -> None:
    publish_event(
        scan_id,
        "module_progress",
        {"module": module, "progress": progress, **extra},
    )


def publish_module_complete(scan_id: str, module: str, result: dict[str, Any] | None = None) -> None:
    publish_event(
        scan_id,
        "module_complete",
        {
            "module": module,
            "message": f"{module} finished",
            "result_preview": result or {},
        },
    )


def publish_module_error(scan_id: str, module: str, error: str) -> None:
    publish_event(
        scan_id,
        "module_error",
        {"module": module, "error": error},
    )
