"""Cohere text client (modality)."""

from typing import Any

from celeste.messages import (
    message_parts,
    request_messages,
    require_part,
    tool_result_object,
)
from celeste.parameters import ParameterMapper
from celeste.providers.cohere.chat.client import CohereChatClient
from celeste.providers.cohere.chat.streaming import (
    CohereChatStream as _CohereChatStream,
)
from celeste.tools import ToolResult
from celeste.types import ImagePart, TextContent, TextPart
from celeste.utils import build_data_url

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

        def cohere_content(content: Any) -> Any:
            if isinstance(content, str):
                return content
            items: list[dict[str, Any]] = []
            for part in message_parts(content):
                require_part("Cohere", part, (TextPart, ImagePart))
                if isinstance(part, TextPart):
                    items.append({"type": "text", "text": part.text})
                elif isinstance(part, ImagePart):
                    items.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": build_data_url(part.image)},
                        }
                    )
            return items

        messages = []
        for message in request_messages(
            prompt=inputs.prompt,
            messages=inputs.messages,
            image=inputs.image,
            video=inputs.video,
            audio=inputs.audio,
            document=inputs.document,
        ):
            if isinstance(message, ToolResult):
                msg = message.model_dump(
                    exclude={"content"},
                    exclude_none=True,
                    mode="json",
                    serialize_as_any=True,
                )
                msg["content"] = tool_result_object(message)
            else:
                msg = message.model_dump(
                    exclude={"content", "tool_calls", "reasoning", "signature"},
                    exclude_none=True,
                    mode="json",
                    serialize_as_any=True,
                )
                msg["content"] = cohere_content(message.content)
            messages.append(msg)
        return {"messages": messages}

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
