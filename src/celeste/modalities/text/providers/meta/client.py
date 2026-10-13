"""Meta text client (OpenResponses protocol)."""

from typing import ClassVar

from celeste.modalities.text.protocols.openresponses.client import (
    OpenResponsesTextClient,
    OpenResponsesTextStream,
)
from celeste.parameters import ParameterMapper
from celeste.providers.meta.responses.config import BASE_URL
from celeste.types import TextContent

from .parameters import META_PARAMETER_MAPPERS


class MetaTextClient(OpenResponsesTextClient):
    """Meta - OpenResponses with default https://api.meta.ai."""

    _default_base_url: ClassVar[str] = BASE_URL

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return META_PARAMETER_MAPPERS


MetaTextStream = OpenResponsesTextStream

__all__ = ["MetaTextClient", "MetaTextStream"]
