import base64
from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from celeste import Modality, create_client
from celeste.artifacts import ImageArtifact
from celeste.auth import NoAuth
from celeste.exceptions import (
    ConstraintViolationError,
    StreamNotExhaustedError,
    ValidationError,
)
from celeste.mime_types import ImageMimeType
from celeste.modalities.images.io import ImageInput
from celeste.modalities.images.providers.byteplus.client import BytePlusImagesStream


def test_pro_exact_dimensions_need_no_sixteen_pixel_alignment() -> None:
    client = create_client(
        modality=Modality.IMAGES,
        model="dola-seedream-5-0-pro-260628",
        auth=NoAuth(),
    )
    inputs = ImageInput(prompt="A red circle")
    request = client._build_request(inputs, aspect_ratio="1500x1000")
    assert request["size"] == "1500x1000"
    for size in ("512x512", "4096x4096", "4096x240"):
        with pytest.raises(ConstraintViolationError):
            client._build_request(inputs, aspect_ratio=size)


@pytest.mark.parametrize("field", ["data", "images"])
@pytest.mark.parametrize("count", [1, 2])
async def test_unary_retains_all_images_and_native_metadata(
    field: str, count: int
) -> None:
    client = create_client(
        modality=Modality.IMAGES, model="dola-seedream-5-0-pro-260628", auth=NoAuth()
    )
    images = [
        {
            "url": "https://example.com/first",
            "output_format": "jpeg",
            "size": "1024x1024",
            "z_index": 0,
        },
        {
            "b64_json": "YWJj",
            "output_format": "png",
            "size": "1024x1024",
            "z_index": 1,
            "bounding_box": [0, 0, 100, 100],
            "name": "foreground",
            "description": "layer",
        },
    ][:count]
    response = {
        field: [*images, {"error": {"code": "failed"}}],
        "model": "response-model",
        "usage": {"generated_images": count, "output_tokens": 12},
    }
    with patch.object(client, "_make_request", new=AsyncMock(return_value=response)):
        output = await client.generate("draw")
    assert isinstance(output.content, ImageArtifact if count == 1 else list)
    artifacts = output.content if isinstance(output.content, list) else [output.content]
    assert artifacts[0].url == "https://example.com/first"
    assert artifacts[0].mime_type == ImageMimeType.JPEG
    for artifact, original in zip(artifacts, images, strict=True):
        assert artifact.metadata == {
            key: value
            for key, value in original.items()
            if key not in {"url", "b64_json"}
        }
    if count == 2:
        assert artifacts[1].data == b"abc"
        assert artifacts[1].mime_type == ImageMimeType.PNG
    assert output.usage is not None
    assert (output.usage.num_images, output.usage.output_tokens) == (count, 12)
    assert output.metadata["raw_response"]["usage"] == response["usage"]
    assert field not in output.metadata["raw_response"]


@pytest.mark.parametrize(
    ("image", "expected_mime"),
    [
        ({"url": "https://example.com/image.png"}, None),
        ({"url": "https://example.com/image", "output_format": "unknown"}, None),
        ({"b64_json": "YWJj"}, None),
        (
            {"b64_json": base64.b64encode(b"\xff\xd8\xff\xe0" + b"\0" * 20).decode()},
            ImageMimeType.JPEG,
        ),
        (
            {
                "b64_json": base64.b64encode(
                    b"\x89PNG\r\n\x1a\n" + b"\0" * 20
                ).decode(),
                "output_format": "unknown",
            },
            ImageMimeType.PNG,
        ),
    ],
)
def test_image_mime_uses_declared_format_or_bytes(
    image: dict[str, Any], expected_mime: ImageMimeType | None
) -> None:
    client = create_client(
        modality=Modality.IMAGES, model="dola-seedream-5-0-pro-260628", auth=NoAuth()
    )
    artifact = client._parse_content({"data": [image]})
    assert isinstance(artifact, ImageArtifact)
    assert artifact.mime_type == expected_mime


@pytest.mark.parametrize("response", [{}, {"data": []}, {"images": []}])
def test_empty_unary_response_still_raises(response: dict[str, Any]) -> None:
    client = create_client(
        modality=Modality.IMAGES, model="dola-seedream-5-0-pro-260628", auth=NoAuth()
    )
    with pytest.raises(ValueError, match="No images or data"):
        client._parse_content(response)


def test_unary_response_without_a_payload_still_raises() -> None:
    client = create_client(
        modality=Modality.IMAGES, model="dola-seedream-5-0-pro-260628", auth=NoAuth()
    )
    with pytest.raises(ValidationError, match="No image URL or base64"):
        client._parse_content(
            {"data": [{"url": "", "b64_json": ""}, {"error": {"code": "failed"}}]}
        )


async def _events(events: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
    for event in events:
        yield event


@pytest.mark.parametrize("success_count", [0, 1, 2])
@pytest.mark.parametrize("include_failure", [False, True])
async def test_stream_retains_images_and_completion(
    success_count: int, include_failure: bool
) -> None:
    successes = [
        {
            "type": "image_generation.partial_succeeded",
            "url": "https://example.com/first",
            "image_index": 1,
            "output_format": "jpeg",
            "size": "1024x1024",
        },
        {
            "type": "image_generation.partial_succeeded",
            "b64_json": "YWJj",
            "image_index": 0,
            "output_format": "png",
        },
    ][:success_count]
    failure = {
        "type": "image_generation.partial_failed",
        "image_index": 2,
        "error": {"code": "blocked", "message": "Blocked"},
    }
    completed = {
        "type": "image_generation.completed",
        "model": "response-model",
        "usage": {"generated_images": success_count, "output_tokens": 12},
    }
    if success_count == 0:
        completed["error"] = {"code": "no_images", "message": "No images generated"}
    events = [*successes, *([failure] if include_failure else []), completed]
    stream = BytePlusImagesStream(_events(events))
    chunks = [chunk async for chunk in stream]
    output = stream.output
    assert len(chunks) == len(events)
    assert all(isinstance(chunk.content, ImageArtifact) for chunk in chunks)
    assert not chunks[-1].content.has_content
    assert chunks[-1].metadata["event_data"] == completed
    assert output.usage is not None
    assert (output.usage.num_images, output.usage.output_tokens) == (success_count, 12)
    assert (
        output.finish_reason is not None and output.finish_reason.reason == "completed"
    )
    assert output.metadata["raw_response"] == completed
    assert "https://example.com/first" not in repr(output.metadata)
    if success_count == 0:
        assert (
            isinstance(output.content, ImageArtifact) and not output.content.has_content
        )
    else:
        assert isinstance(output.content, ImageArtifact if success_count == 1 else list)
        artifacts = (
            output.content if isinstance(output.content, list) else [output.content]
        )
        assert artifacts[0].url == "https://example.com/first"
        assert artifacts[0].mime_type == ImageMimeType.JPEG
        assert artifacts[0].metadata["image_index"] == 1
        assert artifacts[0].metadata["size"] == "1024x1024"
        assert "url" not in artifacts[0].metadata
        if success_count == 2:
            assert artifacts[1].data == b"abc"
            assert artifacts[1].metadata["image_index"] == 0
            assert artifacts[1].mime_type == ImageMimeType.PNG
    if include_failure:
        assert chunks[-2].metadata["error"] == failure["error"]
        assert failure in output.metadata["raw_events"]


async def test_completion_without_usage_still_produces_output() -> None:
    completed = {"type": "image_generation.completed", "error": {"code": "blocked"}}
    stream = BytePlusImagesStream(_events([completed]))
    assert len([chunk async for chunk in stream]) == 1
    assert isinstance(stream.output.content, ImageArtifact)
    assert not stream.output.content.has_content
    assert (
        stream.output.finish_reason is not None
        and stream.output.finish_reason.reason == "completed"
    )
    assert stream.output.usage is not None and stream.output.usage.num_images is None
    assert completed in stream.output.metadata["raw_events"]


async def test_stream_without_meaningful_events_keeps_base_behavior() -> None:
    stream = BytePlusImagesStream(
        _events(
            [
                {"type": "ping"},
                {"type": "image_generation.partial_succeeded", "url": ""},
            ]
        )
    )
    assert [chunk async for chunk in stream] == []
    with pytest.raises(StreamNotExhaustedError):
        _ = stream.output
