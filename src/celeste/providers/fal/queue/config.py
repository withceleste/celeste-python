"""Configuration for fal.ai queue API."""

from enum import StrEnum


class FalQueueEndpoint(StrEnum):
    """Endpoints for fal.ai queue API."""

    RUN = "/{model_id}"


BASE_URL = "https://queue.fal.run"

POLLING_INTERVAL = 0.5
POLLING_TIMEOUT = 120.0
