"""Helpers for canonical chat message content."""

import json

from pydantic import BaseModel

from celeste.core import InputType
from celeste.tools import ToolResult
from celeste.types import (
    AudioContent,
    AudioPart,
    DocumentContent,
    DocumentPart,
    ImageContent,
    ImagePart,
    Message,
    MessageContent,
    MessagePart,
    Role,
    TextPart,
    VideoContent,
    VideoPart,
)


def _as_list[T](value: T | list[T] | None) -> list[T]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def message_parts(content: MessageContent) -> list[MessagePart]:
    """Return message content as an ordered list of content parts."""
    if isinstance(content, str):
        return [TextPart(text=content)]
    return content


def _message_media_types(messages: list[Message | ToolResult] | None) -> set[InputType]:
    """Collect media input types present in normal chat messages."""
    media_types: set[InputType] = set()
    for message in messages or []:
        if isinstance(message, ToolResult):
            continue
        for part in message_parts(message.content):
            if part.type != InputType.TEXT:
                media_types.add(part.type)
    return media_types


def media_types(
    *,
    messages: list[Message | ToolResult] | None = None,
    image: ImageContent | None = None,
    video: VideoContent | None = None,
    audio: AudioContent | None = None,
    document: DocumentContent | None = None,
) -> set[InputType]:
    """Collect media input types from messages and top-level media kwargs."""
    media_types = _message_media_types(messages)
    if _as_list(image):
        media_types.add(InputType.IMAGE)
    if _as_list(video):
        media_types.add(InputType.VIDEO)
    if _as_list(audio):
        media_types.add(InputType.AUDIO)
    if _as_list(document):
        media_types.add(InputType.DOCUMENT)
    return media_types


def _user_message(
    *,
    prompt: str | None = None,
    image: ImageContent | None = None,
    video: VideoContent | None = None,
    audio: AudioContent | None = None,
    document: DocumentContent | None = None,
) -> Message | None:
    """Build a user message from prompt plus top-level media kwargs."""
    images = _as_list(image)
    videos = _as_list(video)
    audios = _as_list(audio)
    documents = _as_list(document)
    has_media = bool(images or videos or audios or documents)

    if not has_media:
        if prompt is None:
            return None
        return Message(role=Role.USER, content=prompt)

    parts: list[MessagePart] = []
    parts.extend(ImagePart(image=item) for item in images)
    parts.extend(VideoPart(video=item) for item in videos)
    parts.extend(AudioPart(audio=item) for item in audios)
    parts.extend(DocumentPart(document=item) for item in documents)
    if prompt is not None:
        parts.append(TextPart(text=prompt))
    return Message(role=Role.USER, content=parts)


def request_messages(
    *,
    prompt: str | None = None,
    messages: list[Message | ToolResult] | None = None,
    image: ImageContent | None = None,
    video: VideoContent | None = None,
    audio: AudioContent | None = None,
    document: DocumentContent | None = None,
) -> list[Message | ToolResult]:
    """Return full request messages, appending top-level media as a user turn."""
    result = list(messages or [])
    extra_message = _user_message(
        prompt=prompt,
        image=image,
        video=video,
        audio=audio,
        document=document,
    )
    if extra_message is not None:
        result.append(extra_message)
    if not result:
        msg = "Text request requires prompt, messages, or media input"
        raise ValueError(msg)
    return result


def _base_model_list(value: object) -> list[BaseModel] | None:
    if not isinstance(value, list):
        return None
    models: list[BaseModel] = []
    for item in value:
        if not isinstance(item, BaseModel):
            return None
        models.append(item)
    return models


def content_to_text(content: object) -> str:
    """Serialize structured content for text-only message fields."""
    if isinstance(content, str):
        return content
    if isinstance(content, BaseModel):
        return content.model_dump_json()
    models = _base_model_list(content)
    if models is not None:
        return json.dumps([item.model_dump(mode="json") for item in models])
    return json.dumps(content)


def tool_result_object(result: ToolResult) -> object:
    """Serialize tool-result content for provider fields that accept JSON objects."""
    content = result.content
    if isinstance(content, BaseModel):
        return content.model_dump(mode="json")
    models = _base_model_list(content)
    if models is not None:
        return [item.model_dump(mode="json") for item in models]
    return content


def require_part(provider: str, part: MessagePart, allowed: tuple[type, ...]) -> None:
    """Raise when a provider serializer receives an unsupported content part."""
    if not isinstance(part, allowed):
        msg = f"{provider} text messages do not support {part.type} content parts"
        raise ValueError(msg)


__all__ = [
    "content_to_text",
    "media_types",
    "message_parts",
    "request_messages",
    "require_part",
    "tool_result_object",
]
