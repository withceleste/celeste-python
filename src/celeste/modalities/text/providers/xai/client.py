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
    TextInput,
    TextOutput,
)
from ...parameters import TextParameters
from ...streaming import TextStream
from ..openresponses.client import OpenResponsesTextStream
from .parameters import XAI_PARAMETER_MAPPERS


class XAITextStream(_XAIResponsesStream, OpenResponsesTextStream):
    """xAI streaming for text modality."""


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

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return XAITextStream


__all__ = ["XAITextClient", "XAITextStream"]
