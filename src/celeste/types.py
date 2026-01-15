"""Type definitions for Celeste."""

from pydantic import BaseModel

from celeste.artifacts import AudioArtifact, ImageArtifact, VideoArtifact

type JsonValue = (
    str | int | float | bool | None | dict[str, JsonValue] | list[JsonValue]
)

type TextContent = str | JsonValue | BaseModel | list[BaseModel]
type AudioContent = AudioArtifact | list[AudioArtifact]
type ImageContent = ImageArtifact | list[ImageArtifact]
type VideoContent = VideoArtifact | list[VideoArtifact]
type EmbeddingsContent = list[float] | list[list[float]]

__all__ = [
    "AudioContent",
    "EmbeddingsContent",
    "ImageContent",
    "JsonValue",
    "TextContent",
    "VideoContent",
]
