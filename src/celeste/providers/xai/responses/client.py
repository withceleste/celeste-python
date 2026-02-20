"""xAI Responses API client."""

from typing import ClassVar

from celeste.protocols.openresponses.client import OpenResponsesClient

from . import config


class XAIResponsesClient(OpenResponsesClient):
    """XAI Responses API client."""

    _default_base_url: ClassVar[str] = config.BASE_URL


__all__ = ["XAIResponsesClient"]
