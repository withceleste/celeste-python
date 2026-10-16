"""Configuration for BFL FLUX API."""

from enum import StrEnum


class BFLFluxEndpoint(StrEnum):
    """Endpoints for BFL FLUX API."""

    CREATE_IMAGE = "/v1/{model_id}"


BASE_URL = "https://api.bfl.ai"

# Polling Configuration
POLLING_INTERVAL = 0.5  # seconds between polling attempts
POLLING_TIMEOUT = 120.0  # 2 minutes timeout
