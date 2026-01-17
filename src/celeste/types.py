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

type Content = str | JsonValue | dict[str, Any] | list[JsonValue | dict[str, Any]]


class Role(StrEnum):
    """Message role in a conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    DEVELOPER = "developer"


class Message(BaseModel):
    """A message in a conversation."""

    model_config = ConfigDict(extra="allow")

    role: Role
    content: Content


__all__ = [
    "AudioContent",
    "Content",
    "EmbeddingsContent",
    "ImageContent",
    "JsonValue",
    "Message",
    "Role",
    "TextContent",
    "VideoContent",
]
