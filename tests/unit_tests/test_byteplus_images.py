"""BytePlus Images request, response, and stream contracts."""

import base64
from collections.abc import AsyncIterator
from typing import Any, ClassVar

import pytest
from pydantic import SecretStr

from celeste.artifacts import ImageArtifact
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.exceptions import (
    ConstraintViolationError,
    StreamEventError,
    ValidationError,
)
from celeste.mime_types import ImageMimeType
from celeste.modalities.images.io import ImageInput
from celeste.modalities.images.parameters import ImageParameter
from celeste.modalities.images.providers.byteplus.client import (
    BytePlusImagesClient,
    BytePlusImagesStream,
)
from celeste.modalities.images.providers.byteplus.models import MODELS
from celeste.models import Model
from celeste.providers.byteplus.images import config

_MODELS = {model.id: model for model in MODELS}
_LITE = _MODELS["seedream-5-0-260128"]
_LITE_ALIAS = _MODELS["seedream-5-0-lite-260128"]
_PRO = _MODELS["dola-seedream-5-0-pro-260628"]


def _client(
    model: Model = _LITE, *, base_url: str | None = None
) -> BytePlusImagesClient:
    return BytePlusImagesClient(
        model=model,
        provider=Provider.BYTEPLUS,
        auth=AuthHeader(secret=SecretStr("test")),
        base_url=base_url,
    )


async def _events(items: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
    for item in items:
        yield item


def test_catalog_matches_current_seedream_image_operations() -> None:
    assert set(_MODELS) == {
        "seedream-4-0-250828",
        "seedream-4-5-251128",
        "seedream-5-0-260128",
        "seedream-5-0-lite-260128",
        "dola-seedream-5-0-pro-260628",
    }
    assert all(
        model.operations[Modality.IMAGES] == {Operation.GENERATE, Operation.EDIT}
        for model in MODELS
    )
    assert _PRO.streaming is False
    assert _PRO.parameter_constraints[ImageParameter.QUALITY].options == [
        "1K",
        "1.5K",
        "2K",
    ]


def test_lite_alias_keeps_its_exact_wire_identity() -> None:
    request = _client(_LITE_ALIAS)._build_request(ImageInput(prompt="generate"))

    assert request["model"] == "seedream-5-0-lite-260128"


def test_edit_serializes_primary_then_ordered_references() -> None:
    primary = ImageArtifact(data=b"primary", mime_type=ImageMimeType.PNG)
    reference = ImageArtifact(url="https://example.com/reference.jpg")

    request = _client(_PRO)._build_request(
        ImageInput(prompt="edit", image=primary),
        reference_images=[reference],
        output_format="png",
        background="transparent",
    )

    assert request["image"] == [
        f"data:image/png;base64,{base64.b64encode(b'primary').decode()}",
        reference.url,
    ]
    assert request["output_format"] == "png"
    assert request["background"] == "transparent"


def test_edit_enforces_total_input_image_limit() -> None:
    primary = ImageArtifact(url="https://example.com/primary.png")
    references = [
        ImageArtifact(url=f"https://example.com/reference-{index}.png")
        for index in range(10)
    ]

    with pytest.raises(ConstraintViolationError, match="at most 10 total"):
        _client(_PRO)._build_request(
            ImageInput(prompt="edit", image=primary),
            reference_images=references,
        )


def test_empty_reference_images_leave_generation_request_unchanged() -> None:
    request = _client()._build_request(
        ImageInput(prompt="generate"), reference_images=[]
    )

    assert "image" not in request


def test_size_class_and_exact_dimensions_are_mutually_exclusive_when_streaming() -> (
    None
):
    with pytest.raises(ConstraintViolationError, match="Cannot use both"):
        _client()._build_request(
            ImageInput(prompt="generate"),
            streaming=True,
            aspect_ratio="2048x2048",
            quality="2K",
        )


def test_unary_response_preserves_all_successes_mime_and_item_metadata() -> None:
    client = _client()
    response = {
        "data": [
            {
                "url": "https://example.com/first.jpg",
                "size": "2048x2048",
                "output_format": "jpeg",
            },
            {"error": {"code": "OutputImageSensitiveContentDetected"}},
            {
                "b64_json": base64.b64encode(b"second").decode(),
                "size": "1024x1024",
                "output_format": "png",
                "z_index": 1,
            },
        ],
        "usage": {"generated_images": 2},
    }

    content = client._parse_content(response)
    assert isinstance(content, list)
    assert [image.mime_type for image in content] == [
        ImageMimeType.JPEG,
        ImageMimeType.PNG,
    ]
    assert content[1].metadata["z_index"] == 1

    raw = client._build_metadata(response)["raw_response"]
    assert raw["data"][0] == {"size": "2048x2048", "output_format": "jpeg"}
    assert raw["data"][1]["error"]["code"] == "OutputImageSensitiveContentDetected"
    assert "b64_json" not in raw["data"][2]


def test_unary_all_item_failures_return_an_empty_collection() -> None:
    client = _client()
    response = {
        "data": [
            {"error": {"code": "OutputImageSensitiveContentDetected"}},
            {"error": {"code": "OutputImageSensitiveContentDetected"}},
        ],
        "usage": {"generated_images": 0},
    }

    assert client._parse_content(response) == []
    assert len(client._build_metadata(response)["raw_response"]["data"]) == 2


def test_unary_top_level_error_preserves_provider_details() -> None:
    with pytest.raises(ValidationError, match="InvalidParameter: bad request"):
        _client()._parse_content(
            {
                "error": {
                    "code": "InvalidParameter",
                    "message": "bad request",
                }
            }
        )


async def test_stream_aggregates_complete_images_by_index_and_retains_failures() -> (
    None
):
    events = [
        {
            "type": "image_generation.partial_image",
            "partial_image_index": 0,
            "b64_json": base64.b64encode(b"preview").decode(),
        },
        {
            "type": "image_generation.partial_succeeded",
            "image_index": 1,
            "b64_json": base64.b64encode(b"second").decode(),
            "size": "1024x1024",
            "output_format": "png",
        },
        {
            "type": "image_generation.partial_failed",
            "image_index": 2,
            "error": {"code": "sensitive", "message": "blocked"},
        },
        {
            "type": "image_generation.partial_succeeded",
            "image_index": 0,
            "url": "https://example.com/first.png",
            "size": "1024x1024",
            "output_format": "png",
        },
        {
            "type": "image_generation.completed",
            "usage": {"generated_images": 2, "output_tokens": 8192},
        },
    ]
    stream = BytePlusImagesStream(_events(events))

    chunks = [chunk async for chunk in stream]

    assert len(chunks) == 3
    assert isinstance(stream.output.content, list)
    assert stream.output.content[0].url == "https://example.com/first.png"
    assert stream.output.content[1].data == b"second"
    assert all(image.mime_type is ImageMimeType.PNG for image in stream.output.content)
    assert [image.metadata["image_index"] for image in stream.output.content] == [0, 1]
    assert stream.output.usage.num_images == 2
    assert stream.output.finish_reason is not None
    assert stream.output.finish_reason.reason == "completed"
    raw_events = stream.output.metadata["raw_events"]
    assert raw_events[0]["image_index"] == 2
    assert raw_events[0]["error"]["code"] == "sensitive"
    assert stream.output.metadata["raw_response"]["usage"]["generated_images"] == 2
    assert all("b64_json" not in chunk.metadata["event_data"] for chunk in chunks)


@pytest.mark.parametrize("event_type", ["error", "image_generation.completed"])
async def test_stream_raises_request_level_errors(event_type: str) -> None:
    stream = BytePlusImagesStream(
        _events(
            [
                {
                    "type": event_type,
                    "error": {"code": "invalid_request", "message": "bad request"},
                }
            ]
        )
    )

    with pytest.raises(StreamEventError, match="bad request"):
        _ = [chunk async for chunk in stream]


async def test_stream_internal_partial_failure_is_terminal() -> None:
    stream = BytePlusImagesStream(
        _events(
            [
                {
                    "type": "image_generation.partial_failed",
                    "error": {
                        "code": "InternalServiceError",
                        "message": "try again",
                    },
                }
            ]
        )
    )

    with pytest.raises(StreamEventError, match="try again"):
        _ = [chunk async for chunk in stream]


async def test_stream_requires_terminal_completion_event() -> None:
    stream = BytePlusImagesStream(
        _events(
            [
                {
                    "type": "image_generation.partial_succeeded",
                    "image_index": 0,
                    "url": "https://example.com/truncated.png",
                    "size": "1024x1024",
                    "output_format": "png",
                }
            ]
        )
    )

    with pytest.raises(StreamEventError, match=r"before image_generation\.completed"):
        _ = [chunk async for chunk in stream]


async def test_stream_completion_requires_billable_usage() -> None:
    stream = BytePlusImagesStream(
        _events(
            [
                {
                    "type": "image_generation.partial_succeeded",
                    "image_index": 0,
                    "url": "https://example.com/output.png",
                    "size": "1024x1024",
                },
                {"type": "image_generation.completed"},
            ]
        )
    )

    with pytest.raises(StreamEventError, match=r"usage\.generated_images"):
        _ = [chunk async for chunk in stream]


class _Response:
    is_success = True

    def json(self) -> dict[str, Any]:
        return {"data": [{"url": "https://example.com/output.png"}]}


class _HTTPClient:
    def __init__(self) -> None:
        self.url: str | None = None

    async def post(self, url: str, **_: object) -> _Response:
        self.url = url
        return _Response()


class _RegionalClient(BytePlusImagesClient):
    test_http_client: ClassVar[_HTTPClient] = _HTTPClient()

    @property
    def http_client(self) -> _HTTPClient:
        return self.test_http_client


async def test_custom_region_base_url_is_used() -> None:
    client = _RegionalClient(
        model=_LITE,
        provider=Provider.BYTEPLUS,
        auth=AuthHeader(secret=SecretStr("test")),
        base_url="https://ark.eu-west.bytepluses.com/api/v3",
    )

    await client._make_request({}, endpoint=config.BytePlusImagesEndpoint.CREATE_IMAGE)

    assert client.test_http_client.url == (
        "https://ark.eu-west.bytepluses.com/api/v3/images/generations"
    )
