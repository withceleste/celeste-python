"""Type definitions for Celeste."""

from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from celeste.artifacts import (
    AudioArtifact,
    DocumentArtifact,
    ImageArtifact,
    VideoArtifact,
)
from celeste.core import InputType

type JsonValue = (
    str | int | float | bool | dict[str, JsonValue] | list[JsonValue] | None
)

type TextContent = str | JsonValue | BaseModel | list[BaseModel]
type ToolResultContent = TextContent
type AudioContent = AudioArtifact | list[AudioArtifact]
type DocumentContent = DocumentArtifact | list[DocumentArtifact]
type ImageContent = ImageArtifact | list[ImageArtifact]
type VideoContent = VideoArtifact | list[VideoArtifact]
type EmbeddingsContent = list[float] | list[list[float]]

type RawUsage = dict[str, int | float | None]


class TextPart(BaseModel):
    """Text block inside a chat message."""

    type: Literal[InputType.TEXT] = InputType.TEXT
    text: str


class ImagePart(BaseModel):
    """Image block inside a chat message."""

    type: Literal[InputType.IMAGE] = InputType.IMAGE
    image: ImageArtifact


class AudioPart(BaseModel):
    """Audio block inside a chat message."""

    type: Literal[InputType.AUDIO] = InputType.AUDIO
    audio: AudioArtifact


class VideoPart(BaseModel):
    """Video block inside a chat message."""

    type: Literal[InputType.VIDEO] = InputType.VIDEO
    video: VideoArtifact


class DocumentPart(BaseModel):
    """Document block inside a chat message."""

    type: Literal[InputType.DOCUMENT] = InputType.DOCUMENT
    document: DocumentArtifact


type MessagePart = Annotated[
    TextPart | ImagePart | AudioPart | VideoPart | DocumentPart,
    Field(discriminator="type"),
]
type MessageContent = str | list[MessagePart]


class Role(StrEnum):
    """Message role in a conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    DEVELOPER = "developer"


class ToolCall(BaseModel):
    """A tool call returned by the model."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    arguments: dict[str, Any]


class ToolActivityStatus(StrEnum):
    """Lifecycle of a native (server-side) tool invocation during streaming."""

    STARTED = "started"
    COMPLETED = "completed"


class ToolActivity(BaseModel):
    """A native tool invocation surfaced live in a streaming chunk."""

    tool_name: str
    status: ToolActivityStatus


class Message(BaseModel):
    """A message in a conversation."""

    model_config = ConfigDict(extra="allow")

    role: Role
    content: MessageContent
    tool_calls: list[ToolCall] | None = None
    reasoning: str | None = None
    signature: list[dict[str, Any]] | None = None
    container: dict[str, Any] | None = None


__all__ = [
    "AudioContent",
    "AudioPart",
    "DocumentContent",
    "DocumentPart",
    "EmbeddingsContent",
    "ImageContent",
    "ImagePart",
    "JsonValue",
    "Message",
    "MessageContent",
    "MessagePart",
    "RawUsage",
    "Role",
    "TextContent",
    "TextPart",
    "ToolActivity",
    "ToolActivityStatus",
    "ToolCall",
    "ToolResultContent",
    "VideoContent",
    "VideoPart",
]
