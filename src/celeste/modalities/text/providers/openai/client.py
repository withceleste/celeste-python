"""OpenAI text client."""

from celeste.parameters import ParameterMapper
from celeste.providers.openai.responses.client import (
    OpenAIResponsesClient as OpenAIResponsesMixin,
)
from celeste.providers.openai.responses.streaming import (
    OpenAIResponsesStream as _OpenAIResponsesStream,
)
from celeste.types import TextContent

from ...protocols.openresponses.client import (
    OpenResponsesTextClient,
)
from ...protocols.openresponses.client import (
    OpenResponsesTextStream as _OpenResponsesTextStream,
)
from ...streaming import TextStream
from .parameters import OPENAI_PARAMETER_MAPPERS


class OpenAITextStream(_OpenAIResponsesStream, _OpenResponsesTextStream):
    """OpenAI streaming for text modality."""


class OpenAITextClient(OpenAIResponsesMixin, OpenResponsesTextClient):
    """OpenAI text client using Responses API."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return OPENAI_PARAMETER_MAPPERS

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return OpenAITextStream


__all__ = ["OpenAITextClient", "OpenAITextStream"]
