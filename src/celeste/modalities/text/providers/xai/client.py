"""xAI text client (modality)."""

from typing import Any, Unpack

from celeste.parameters import ParameterMapper
from celeste.providers.xai.responses.client import XAIResponsesClient
from celeste.providers.xai.responses.streaming import (
    XAIResponsesStream as _XAIResponsesStream,
)
from celeste.types import ImageContent, Message, TextContent, VideoContent
from celeste.utils import build_image_data_url

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
from .parameters import XAI_PARAMETER_MAPPERS


class XAITextStream(_XAIResponsesStream, TextStream):
    """xAI streaming for text modality."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._response_data: dict[str, Any] | None = None

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
        event_type = event_data.get("type")
        if event_type == "response.completed":
            response = event_data.get("response")
            if isinstance(response, dict):
                self._response_data = response

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
        """Collect raw events (filtering happens in _build_stream_metadata)."""
        events: list[dict[str, Any]] = []
        if self._response_data is not None:
            events.append(self._response_data)
        for chunk in chunks:
            event_data = chunk.metadata.get("event_data")
            if isinstance(event_data, dict):
                events.append(event_data)
        return events


class XAITextClient(XAIResponsesClient, TextClient):
    """xAI text client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return XAI_PARAMETER_MAPPERS

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

    async def analyze(
        self,
        prompt: str | None = None,
        *,
        messages: list[Message] | None = None,
        image: ImageContent | None = None,
        video: VideoContent | None = None,
        **parameters: Unpack[TextParameters],
    ) -> TextOutput:
        """Analyze image(s) or video(s) with prompt or messages."""
        inputs = TextInput(prompt=prompt, messages=messages, image=image, video=video)
        return await self._predict(inputs, **parameters)

    def _init_request(self, inputs: TextInput) -> dict[str, Any]:
        """Initialize request from XAI Responses API format."""
        if inputs.messages is not None:
            return {"input": [message.model_dump() for message in inputs.messages]}

        if inputs.image is None:
            return {"input": inputs.prompt or ""}

        # Multimodal: build content array with images + text
        images = inputs.image if isinstance(inputs.image, list) else [inputs.image]
        content: list[dict[str, Any]] = []
        for img in images:
            content.append(
                {"type": "input_image", "image_url": build_image_data_url(img)}
            )
        content.append({"type": "input_text", "text": inputs.prompt or ""})

        return {"input": [{"role": "user", "content": content}]}

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
        output = super()._parse_content(response_data)
        for item in output:
            if item.get("type") == "message":
                for part in item.get("content", []):
                    if part.get("type") == "output_text":
                        text = part.get("text") or ""
                        return self._transform_output(text, **parameters)

        return self._transform_output("", **parameters)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> TextFinishReason:
        """Parse finish reason from response."""
        finish_reason = super()._parse_finish_reason(response_data)
        return TextFinishReason(reason=finish_reason.reason)

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return XAITextStream


__all__ = ["XAITextClient", "XAITextStream"]
