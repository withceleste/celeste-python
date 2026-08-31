"""xAI-specific text IO types."""

from typing import cast

from pydantic import Field, SerializeAsAny, model_validator

from celeste.messages import content_to_text
from celeste.types import (
    ImagePart,
    Message,
    MessageContent,
    Role,
    TextContent,
    TextPart,
)

from ...io import TextOutput, TextUsage


class XAITextUsage(TextUsage):
    """xAI text usage, including context-compaction telemetry."""

    dropped_message_count: int | None = None


class XAITextOutput(TextOutput):
    """xAI text output, including native generated images."""

    content: SerializeAsAny[TextContent]
    usage: XAITextUsage = Field(default_factory=XAITextUsage)

    @model_validator(mode="before")
    @classmethod
    def _restore_image_content(cls, data: object) -> object:
        """Restore serialized image output without interpreting structured JSON."""
        if not isinstance(data, dict):
            return data
        content = data.get("content")
        signature = data.get("signature")
        if (
            isinstance(content, list)
            and isinstance(signature, list)
            and any(
                isinstance(item, dict) and item.get("type") == "image_generation_call"
                for item in signature
            )
        ):
            data = dict(data)
            data["content"] = Message(role=Role.ASSISTANT, content=content).content
        return data

    @property
    def message(self) -> Message:
        """Preserve generated image parts in the assistant message."""
        content = (
            cast(MessageContent, self.content)
            if isinstance(self.content, list)
            and self.content
            and all(isinstance(part, (TextPart, ImagePart)) for part in self.content)
            else content_to_text(self.content)
        )
        return Message(
            role=Role.ASSISTANT,
            content=content,
            tool_calls=self.tool_calls if self.tool_calls else None,
            reasoning=self.reasoning,
            signature=self.signature,
            container=self.container,
        )


__all__ = ["XAITextOutput", "XAITextUsage"]
