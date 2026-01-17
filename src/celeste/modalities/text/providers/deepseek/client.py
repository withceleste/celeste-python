"""DeepSeek text client (modality)."""

from typing import Any, Unpack

from celeste.parameters import ParameterMapper
from celeste.providers.deepseek.chat.client import DeepSeekChatClient
from celeste.providers.deepseek.chat.streaming import (
    DeepSeekChatStream as _DeepSeekChatStream,
)
from celeste.types import Message, TextContent

from ...client import TextClient
from ...io import (
    TextChunk,
    TextFinishReason,
    TextInput,
    TextOutput,
    TextUsage,
)
from ...parameters import TextParameters
from ...streaming import TextStream
from .parameters import DEEPSEEK_PARAMETER_MAPPERS


class DeepSeekTextStream(_DeepSeekChatStream, TextStream):
    """DeepSeek streaming for text modality."""

    def _parse_chunk_usage(self, event_data: dict[str, Any]) -> TextUsage | None:
        """Parse and wrap usage from SSE event."""
        usage = super()._parse_chunk_usage(event_data)
        if usage:
            return TextUsage(**usage)
        return None

    def _parse_chunk_finish_reason(
        self, event_data: dict[str, Any]
    ) -> TextFinishReason | None:
        """Parse and wrap finish reason from SSE event."""
        finish_reason = super()._parse_chunk_finish_reason(event_data)
        if finish_reason:
            return TextFinishReason(reason=finish_reason.reason)
        return None

    def _parse_chunk(self, event_data: dict[str, Any]) -> TextChunk | None:
        """Parse one SSE event into a typed chunk."""
        content = self._parse_chunk_content(event_data)
        if content is None:
            usage = self._parse_chunk_usage(event_data)
            finish_reason = self._parse_chunk_finish_reason(event_data)
            if usage is None and finish_reason is None:
                return None
            content = ""

        return TextChunk(
            content=content,
            finish_reason=self._parse_chunk_finish_reason(event_data),
            usage=self._parse_chunk_usage(event_data),
            metadata={"event_data": event_data},
        )

    def _aggregate_content(self, chunks: list[TextChunk]) -> str:
        """Aggregate streamed text content."""
        return "".join(chunk.content for chunk in chunks)

    def _aggregate_event_data(self, chunks: list[TextChunk]) -> list[dict[str, Any]]:
        """Collect metadata events."""
        events: list[dict[str, Any]] = []
        for chunk in chunks:
            event_data = chunk.metadata.get("event_data")
            if isinstance(event_data, dict):
                events.append(event_data)
        return events


class DeepSeekTextClient(DeepSeekChatClient, TextClient):
    """DeepSeek text client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return DEEPSEEK_PARAMETER_MAPPERS

    async def generate(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        """Generate text from prompt."""
        inputs = TextInput(prompt=prompt, messages=messages)
        return await self._predict(inputs, **parameters)

    def _init_request(self, inputs: TextInput) -> dict[str, Any]:
        """Initialize request from DeepSeek messages array format."""
        # If messages provided, use them directly (messages take precedence)
        if inputs.messages is not None:
            return {"messages": [message.model_dump() for message in inputs.messages]}

        # Fall back to prompt-based input
        messages = [
            {
                "role": "user",
                "content": inputs.prompt or "",
            }
        ]

        return {"messages": messages}

    def _parse_usage(self, response_data: dict[str, Any]) -> TextUsage:
        """Parse usage from response."""
        usage = super()._parse_usage(response_data)
        return TextUsage(**usage)

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[TextParameters],
    ) -> TextContent:
        """Parse content from response."""
        choices = super()._parse_content(response_data)
        message = choices[0].get("message", {})
        content = message.get("content") or ""
        return self._transform_output(content, **parameters)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> TextFinishReason:
        """Parse finish reason from response."""
        finish_reason = super()._parse_finish_reason(response_data)
        return TextFinishReason(reason=finish_reason.reason)

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return DeepSeekTextStream


__all__ = ["DeepSeekTextClient", "DeepSeekTextStream"]
