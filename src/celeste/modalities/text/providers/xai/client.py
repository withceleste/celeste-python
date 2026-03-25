"""xAI text client (modality)."""

from typing import Any

from celeste.parameters import ParameterMapper
from celeste.providers.xai.responses.client import XAIResponsesClient
from celeste.providers.xai.responses.streaming import (
    XAIResponsesStream as _XAIResponsesStream,
)
from celeste.types import TextContent

from ...io import TextInput
from ...protocols.openresponses.client import (
    OpenResponsesTextClient,
)
from ...protocols.openresponses.client import (
    OpenResponsesTextStream as _OpenResponsesTextStream,
)
from ...streaming import TextStream
from .parameters import XAI_PARAMETER_MAPPERS


class XAITextStream(_XAIResponsesStream, _OpenResponsesTextStream):
    """xAI streaming for text modality."""


class XAITextClient(XAIResponsesClient, OpenResponsesTextClient):
    """xAI text client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return XAI_PARAMETER_MAPPERS

    def _init_request(self, inputs: TextInput) -> dict[str, Any]:
        """xAI accepts plain string input for text-only requests."""
        if inputs.messages is None and inputs.image is None:
            return {"input": inputs.prompt or ""}
        return super()._init_request(inputs)

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return XAITextStream


__all__ = ["XAITextClient", "XAITextStream"]
