"""OpenAI Responses API client."""

from typing import ClassVar

from celeste.protocols.openresponses.client import OpenResponsesClient

from . import config


class OpenAIResponsesClient(OpenResponsesClient):
    """OpenAI Responses API client."""

    _default_base_url: ClassVar[str] = config.BASE_URL


__all__ = ["OpenAIResponsesClient"]
