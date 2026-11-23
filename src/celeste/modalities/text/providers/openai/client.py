"""OpenAI text client."""

from typing import Any, Unpack

from celeste.parameters import ParameterMapper
from celeste.protocols.openresponses.tools import native_replay_output
from celeste.providers.openai.auth import ChatGPT
from celeste.providers.openai.responses.client import (
    OpenAIResponsesClient as OpenAIResponsesMixin,
)
from celeste.providers.openai.responses.streaming import (
    OpenAIResponsesStream as _OpenAIResponsesStream,
)
from celeste.types import Role, TextContent

from ...io import TextChunk, TextInput, TextOutput
from ...parameters import TextParameters
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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._items: dict[int, dict[str, Any]] = {}

    def _parse_chunk(self, event_data: dict[str, Any]) -> TextChunk | None:
        """Parse one SSE event; a terminal response without output takes the items streamed before it."""
        if event_data.get("type") == "response.output_item.done":
            self._items[event_data["output_index"]] = event_data["item"]
        chunk = super()._parse_chunk(event_data)
        if self._response_data is not None and not self._response_data.get("output"):
            self._response_data = {
                **self._response_data,
                "output": [self._items[index] for index in sorted(self._items)],
            }
        return chunk

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
        if isinstance(self.auth, ChatGPT):
            # ChatGPT sign-in stores nothing, so reasoning returns encrypted for the next turn to resend.
            request["store"] = False
            request["include"] = ["reasoning.encrypted_content"]
            # It rejects system messages and takes the system prompt as developer messages.
            for item in request["input"]:
                if item.get("role") == Role.SYSTEM:
                    item["role"] = Role.DEVELOPER.value
        return request

    async def _predict(
        self,
        inputs: TextInput,
        *,
        endpoint: str | None = None,
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        """Predict; ChatGPT sign-in only streams, so the stream is read to its end."""
        if not isinstance(self.auth, ChatGPT):
            return await super()._predict(
                inputs,
                endpoint=endpoint,
                extra_body=extra_body,
                extra_headers=extra_headers,
                **parameters,
            )
        stream = self._stream(
            inputs,
            self._stream_class(),
            endpoint=endpoint,
            extra_body=extra_body,
            extra_headers=extra_headers,
            **parameters,
        )
        async for _ in stream:
            pass
        return stream.output

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
