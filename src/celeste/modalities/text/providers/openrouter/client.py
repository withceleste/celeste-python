"""OpenRouter text client (OpenResponses protocol)."""

from typing import ClassVar

from celeste.modalities.text.protocols.openresponses.client import (
    OpenResponsesTextClient,
    OpenResponsesTextStream,
)
from celeste.parameters import ParameterMapper
from celeste.providers.openrouter.responses.config import BASE_URL
from celeste.types import TextContent

from .parameters import OPENROUTER_PARAMETER_MAPPERS


class OpenRouterTextClient(OpenResponsesTextClient):
    """OpenRouter — OpenResponses with default https://openrouter.ai/api."""

    _default_base_url: ClassVar[str] = BASE_URL

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return OPENROUTER_PARAMETER_MAPPERS


OpenRouterTextStream = OpenResponsesTextStream

__all__ = ["OpenRouterTextClient", "OpenRouterTextStream"]
