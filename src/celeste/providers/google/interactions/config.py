"""Configuration for Google Interactions API."""

from enum import StrEnum


class GoogleInteractionsEndpoint(StrEnum):
    """Endpoints for Google Interactions API."""

    # v1beta: /v1 serves only stable models (preview ids 404 there)
    CREATE_INTERACTION = "/v1beta/interactions"


BASE_URL = "https://generativelanguage.googleapis.com"
