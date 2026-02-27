"""Type definitions for Celeste."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict

from celeste.artifacts import AudioArtifact, ImageArtifact, VideoArtifact

type JsonValue = (
    str | int | float | bool | None | dict[str, JsonValue] | list[JsonValue]
)

type TextContent = str | JsonValue | BaseModel | list[BaseModel]
type AudioContent = AudioArtifact | list[AudioArtifact]
type ImageContent = ImageArtifact | list[ImageArtifact]
type VideoContent = VideoArtifact | list[VideoArtifact]
type EmbeddingsContent = list[float] | list[list[float]]

type Content = TextContent | ImageContent | VideoContent | AudioContent

type RawUsage = dict[str, int | float | None]


class Role(StrEnum):
    """Message role in a conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    DEVELOPER = "developer"


class ToolCall(BaseModel):
    """A tool call returned by the model."""

    id: str
    name: str
    arguments: dict[str, Any]


class Message(BaseModel):
    """A message in a conversation."""

    model_config = ConfigDict(extra="allow")

    role: Role
    content: Content
    tool_calls: list[ToolCall] | None = None


__all__ = [
    "AudioContent",
    "Content",
    "EmbeddingsContent",
    "ImageContent",
    "JsonValue",
    "Message",
    "RawUsage",
    "Role",
    "TextContent",
    "ToolCall",
    "VideoContent",
]
