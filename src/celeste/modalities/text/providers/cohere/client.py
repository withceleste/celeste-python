"""Cohere text client (modality)."""

from typing import Any

from celeste.parameters import ParameterMapper
from celeste.providers.cohere.chat.client import CohereChatClient
from celeste.providers.cohere.chat.streaming import (
    CohereChatStream as _CohereChatStream,
)
from celeste.types import TextContent
from celeste.utils import build_image_data_url

from ...client import TextClient
from ...io import (
    TextInput,
)
from ...streaming import TextStream
from .parameters import COHERE_PARAMETER_MAPPERS


class CohereTextStream(_CohereChatStream, TextStream):
    """Cohere streaming for text modality."""


class CohereTextClient(CohereChatClient, TextClient):
    """Cohere text client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[TextContent]]:
        return COHERE_PARAMETER_MAPPERS

    def _init_request(self, inputs: TextInput) -> dict[str, Any]:
        """Initialize request from Cohere v2 Chat API messages array format."""
        # If messages provided, use them directly (messages take precedence)
        if inputs.messages is not None:
            return {
                "messages": [
                    message.model_dump(exclude_none=True) for message in inputs.messages
                ]
            }

        # Fall back to prompt-based input
        if inputs.image is None:
            content: str | list[dict[str, Any]] = inputs.prompt or ""
        else:
            images = inputs.image if isinstance(inputs.image, list) else [inputs.image]
            content = [
                {
                    "type": "image_url",
                    "image_url": {"url": build_image_data_url(img)},
                }
                for img in images
            ]
            content.append({"type": "text", "text": inputs.prompt or ""})

        return {"messages": [{"role": "user", "content": content}]}

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> TextContent:
        """Parse content from response."""
        content_array = super()._parse_content(response_data)
        first_content = content_array[0]
        text = first_content.get("text") or ""
        return text

    def _stream_class(self) -> type[TextStream]:
        """Return the Stream class for this provider."""
        return CohereTextStream


__all__ = ["CohereTextClient", "CohereTextStream"]
