"""OpenAI text client."""

from typing import Any

from celeste.parameters import ParameterMapper
from celeste.protocols.openresponses.tools import native_replay_output
from celeste.providers.openai.responses.client import (
    OpenAIResponsesClient as OpenAIResponsesMixin,
)
from celeste.providers.openai.responses.streaming import (
    OpenAIResponsesStream as _OpenAIResponsesStream,
)
from celeste.types import TextContent

from ...io import TextChunk, TextInput
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

    def _aggregate_signature(
        self, chunks: list[TextChunk], raw_events: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Return every output item when stateless replay must resend them in order."""
        if self._response_data is None:
            return []
        return native_replay_output(self._response_data.get("output", []))


class OpenAITextClient(OpenAIResponsesMixin, OpenResponsesTextClient):
    """OpenAI text client using Responses API."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return OPENAI_PARAMETER_MAPPERS

    def _init_request(self, inputs: TextInput) -> dict[str, Any]:
        request = super()._init_request(inputs)
        for item in request["input"]:
            if item.get("type") != "function_call_output":
                continue
            # Programmatic tool results must echo their call's caller.
            caller = next(
                (
                    call["caller"]
                    for call in request["input"]
                    if call.get("type") == "function_call"
                    and call.get("call_id") == item["call_id"]
                    and call.get("caller")
                ),
                None,
            )
            if caller:
                item["caller"] = caller
        return request

    def _parse_reasoning(
        self, response_data: dict[str, Any]
    ) -> tuple[str | None, list[dict[str, Any]]]:
        """Parse reasoning; keep every output item when replay must resend them in order."""
        text, _ = super()._parse_reasoning(response_data)
        return text, native_replay_output(response_data.get("output", []))

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return OpenAITextStream


__all__ = ["OpenAITextClient", "OpenAITextStream"]
