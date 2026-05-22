"""Unit tests for canonical multimodal message content."""

import pytest
from pydantic import BaseModel, ValidationError

from celeste import (
    DocumentPart,
    ImagePart,
    Message,
    Role,
    TextPart,
)
from celeste.artifacts import DocumentArtifact, ImageArtifact
from celeste.mime_types import DocumentMimeType, ImageMimeType
from celeste.tools import ToolResult


class StructuredPayload(BaseModel):
    ok: bool


def test_message_content_accepts_ordered_text_and_image_parts() -> None:
    message = Message(
        role=Role.USER,
        content=[
            TextPart(text="describe"),
            ImagePart(image=ImageArtifact(data=b"abc", mime_type=ImageMimeType.PNG)),
        ],
    )

    dumped = message.model_dump(mode="json")

    assert dumped["content"][0] == {"type": "text", "text": "describe"}
    assert dumped["content"][1]["type"] == "image"
    assert dumped["content"][1]["image"]["data"] == "YWJj"
    assert dumped["content"][1]["image"]["mime_type"] == "image/png"


def test_message_content_round_trips_discriminated_document_part() -> None:
    message = Message(
        role=Role.USER,
        content=[
            TextPart(text="summarize"),
            DocumentPart(
                document=DocumentArtifact(
                    data=b"abc",
                    mime_type=DocumentMimeType.PDF,
                )
            ),
        ],
    )

    restored = Message.model_validate_json(message.model_dump_json())

    assert isinstance(restored.content, list)
    assert isinstance(restored.content[0], TextPart)
    assert isinstance(restored.content[1], DocumentPart)
    assert restored.content[1].document.data == b"abc"


def test_message_content_rejects_raw_artifact() -> None:
    with pytest.raises(ValidationError):
        Message(role=Role.USER, content=ImageArtifact(data=b"abc"))


def test_message_content_rejects_mixed_raw_list() -> None:
    with pytest.raises(ValidationError):
        Message(
            role=Role.USER,
            content=["describe", ImageArtifact(data=b"abc")],  # type: ignore[list-item]
        )


def test_message_content_rejects_structured_payload() -> None:
    with pytest.raises(ValidationError):
        Message(role=Role.USER, content=StructuredPayload(ok=True))


def test_tool_result_content_remains_structured_payload() -> None:
    result = ToolResult(
        content=StructuredPayload(ok=True),
        tool_call_id="call_123",
        name="structured_tool",
    )

    assert result.content == StructuredPayload(ok=True)
