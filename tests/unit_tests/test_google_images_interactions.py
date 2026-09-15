"""Unit tests for Google images provider Interactions/Vertex dispatch and wire shape."""

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import SecretStr

from celeste import Model, create_client
from celeste.artifacts import ImageArtifact
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import ImageMimeType
from celeste.modalities.images.io import ImageInput
from celeste.modalities.images.providers.google.client import GoogleImagesClient
from celeste.modalities.images.providers.google.interactions import (
    GoogleInteractionsImagesClient,
)
from celeste.modalities.images.providers.google.vertex import GoogleVertexImagesClient
from celeste.providers.google.auth import GoogleADC


def _model() -> Model:
    return Model(
        id="gemini-3.1-flash-image",
        provider=Provider.GOOGLE,
        display_name="Nano Banana 2",
        operations={Modality.IMAGES: {Operation.GENERATE, Operation.EDIT}},
    )


def _api_key_auth() -> AuthHeader:
    return AuthHeader(secret=SecretStr("test"), header="x-goog-api-key", prefix="")


def test_api_key_auth_dispatches_to_interactions_strategy() -> None:
    client = GoogleImagesClient(
        model=_model(), provider=Provider.GOOGLE, auth=_api_key_auth()
    )
    assert isinstance(client._strategy, GoogleInteractionsImagesClient)
    assert client._generate_endpoint == client._strategy._generate_endpoint
    assert client._edit_endpoint == client._strategy._edit_endpoint


def test_google_adc_auth_dispatches_to_vertex_strategy() -> None:
    client = GoogleImagesClient(
        model=_model(), provider=Provider.GOOGLE, auth=GoogleADC(project_id="p")
    )
    assert isinstance(client._strategy, GoogleVertexImagesClient)
    assert client._generate_endpoint == client._strategy._generate_endpoint
    assert client._edit_endpoint == client._strategy._edit_endpoint


@pytest.mark.parametrize("use_adc", [False, True], ids=["api-key", "adc"])
def test_create_client_rejects_unknown_google_images_model(use_adc: bool) -> None:
    model = Model(
        id="unknown-google-image-model",
        provider=Provider.GOOGLE,
        display_name="Unknown Google image model",
        operations={Modality.IMAGES: {Operation.GENERATE}},
    )
    auth = GoogleADC(project_id="p") if use_adc else _api_key_auth()

    with pytest.raises(ValueError, match="Unknown Google images model"):
        create_client(
            modality=Modality.IMAGES,
            provider=Provider.GOOGLE,
            model=model,
            auth=auth,
        )


def test_interactions_init_request_generate_is_text_only() -> None:
    client = GoogleImagesClient(
        model=_model(), provider=Provider.GOOGLE, auth=_api_key_auth()
    )

    request = client._init_request(ImageInput(prompt="a nano banana dish"))

    assert request == {
        "input": [
            {
                "type": "user_input",
                "content": [{"type": "text", "text": "a nano banana dish"}],
            }
        ],
        "response_format": {"type": "image"},
    }


def test_interactions_init_request_edit_prepends_image_part() -> None:
    client = GoogleImagesClient(
        model=_model(), provider=Provider.GOOGLE, auth=_api_key_auth()
    )

    request = client._init_request(
        ImageInput(
            prompt="add a hat",
            image=ImageArtifact(data=b"abc", mime_type=ImageMimeType.PNG),
        )
    )

    content = request["input"][0]["content"]
    assert request["input"][0]["type"] == "user_input"
    assert content[0]["type"] == "image"
    assert content[0]["data"] == "YWJj"
    assert content[1] == {"type": "text", "text": "add a hat"}


def test_interactions_aspect_ratio_and_quality_map_to_response_format() -> None:
    client = GoogleImagesClient(
        model=_model(), provider=Provider.GOOGLE, auth=_api_key_auth()
    )

    request = client._build_request(
        ImageInput(prompt="a nano banana dish"),
        aspect_ratio="16:9",
        quality="2K",
    )

    assert request["response_format"] == {
        "type": "image",
        "aspect_ratio": "16:9",
        "image_size": "2K",
    }


def test_interactions_reference_images_stay_inside_user_input_content() -> None:
    client = GoogleImagesClient(
        model=_model(), provider=Provider.GOOGLE, auth=_api_key_auth()
    )

    request = client._build_request(
        ImageInput(prompt="combine these"),
        reference_images=[ImageArtifact(data=b"ref", mime_type=ImageMimeType.PNG)],
    )

    assert request["input"][0]["type"] == "user_input"
    content = request["input"][0]["content"]
    assert content[0]["type"] == "image"
    assert content[0]["data"] == "cmVm"
    assert content[1] == {"type": "text", "text": "combine these"}


def test_interactions_parse_content_extracts_image_from_model_output_step() -> None:
    client = GoogleInteractionsImagesClient(
        model=_model(), provider=Provider.GOOGLE, auth=_api_key_auth()
    )

    response_data = {
        "id": "v1_abc",
        "status": "completed",
        "steps": [
            {
                "type": "model_output",
                "content": [
                    {"type": "image", "data": "YWJj", "mime_type": "image/png"}
                ],
            }
        ],
    }

    artifact = client._parse_content(response_data)

    assert isinstance(artifact, ImageArtifact)
    assert artifact.data == b"abc"
    assert artifact.mime_type == ImageMimeType.PNG


@pytest.mark.parametrize("use_adc", [False, True], ids=["interactions", "vertex"])
@pytest.mark.parametrize("operation", ["generate", "edit"])
async def test_public_image_output_retains_order_usage_and_metadata(
    use_adc: bool, operation: str
) -> None:
    client = GoogleImagesClient(
        model=_model(),
        provider=Provider.GOOGLE,
        auth=GoogleADC(project_id="p", location="europe-west4")
        if use_adc
        else _api_key_auth(),
    )
    response: dict[str, Any]
    if use_adc:
        response = {
            "responseId": "response-1",
            "modelVersion": "model-version",
            "usageMetadata": {"promptTokenCount": 3, "candidatesTokenCount": 7},
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "First", "citationMetadata": {"citations": []}},
                            {"inlineData": {"data": "YWJj", "mimeType": "image/png"}},
                            {"inlineData": {"data": "YWJj"}, "thought": True},
                            {"inlineData": {}},
                        ]
                    },
                    "finishReason": "STOP",
                    "finishMessage": "Done",
                    "safetyRatings": [{"category": "safe"}],
                    "groundingMetadata": {"webSearchQueries": ["cats"]},
                },
                {
                    "content": {
                        "parts": [
                            {"text": "Second"},
                            {
                                "fileData": {"fileUri": "https://example.com/image"},
                                "thoughtSignature": "signature",
                            },
                        ]
                    }
                },
            ],
        }
        position_key = "candidate_index"
        usage_key = "usageMetadata"
    else:
        response = {
            "id": "response-1",
            "model": "model-version",
            "status": "completed",
            "usage": {"total_input_tokens": 3, "total_output_tokens": 7},
            "steps": [
                {
                    "type": "model_output",
                    "content": [
                        {
                            "type": "text",
                            "text": "First",
                            "annotations": [
                                {
                                    "type": "url_citation",
                                    "url": "https://example.com/source",
                                }
                            ],
                        },
                        {"type": "image", "data": "YWJj", "mime_type": "image/png"},
                        {"type": "image"},
                    ],
                },
                {
                    "type": "model_output",
                    "content": [
                        {"type": "text", "text": "Second"},
                        {
                            "type": "image",
                            "uri": "https://example.com/image",
                            "signature": "signature",
                        },
                    ],
                },
                {"type": "thought", "content": [{"type": "image", "data": "YWJj"}]},
            ],
        }
        position_key = "step_index"
        usage_key = "usage"
    with patch.object(
        client._strategy, "_make_request", new=AsyncMock(return_value=response)
    ):
        if operation == "edit":
            output = await client.edit(
                ImageArtifact(data=b"input", mime_type=ImageMimeType.PNG), "draw"
            )
        else:
            output = await client.generate("draw")
    assert isinstance(output.content, list)
    first, second = output.content
    assert first.data == b"abc"
    assert first.mime_type == ImageMimeType.PNG
    assert second.url == "https://example.com/image"
    assert second.mime_type is None
    assert [
        (item.metadata[position_key], item.metadata["part_index"])
        for item in output.content
    ] == [(0, 1), (1, 1)]
    assert (
        second.metadata["thoughtSignature" if use_adc else "signature"] == "signature"
    )
    assert output.usage is not None
    assert (
        output.usage.num_images,
        output.usage.input_tokens,
        output.usage.output_tokens,
    ) == (2, 3, 7)
    blocks = output.metadata["text_blocks"]
    assert [
        (block["text"], block[position_key], block["part_index"]) for block in blocks
    ] == [("First", 0, 0), ("Second", 1, 0)]
    raw = output.metadata["raw_response"]
    assert raw[usage_key] == response[usage_key]
    assert "YWJj" not in repr(output.metadata)
    assert "https://example.com/image" not in repr(output.metadata)
    assert output.finish_reason is not None
    if use_adc:
        assert raw["vertex_location"] == "europe-west4"
        assert raw["responseId"] == "response-1"
        assert raw["modelVersion"] == "model-version"
        assert raw["candidates"][0] == {
            key: value
            for key, value in response["candidates"][0].items()
            if key != "content"
        }
        assert blocks[0]["citationMetadata"] == {"citations": []}
        assert (output.finish_reason.reason, output.finish_reason.message) == (
            "STOP",
            "Done",
        )
    else:
        assert raw["id"] == "response-1"
        assert raw["model"] == "model-version"
        assert "steps" not in raw
        assert blocks[0]["annotations"][0]["url"] == "https://example.com/source"
        assert output.finish_reason.reason == "completed"


@pytest.mark.parametrize(
    ("use_adc", "response", "reason"),
    [
        (
            False,
            {
                "steps": [{"type": "model_output", "content": [{"type": "image"}]}],
                "status": "completed",
            },
            "completed",
        ),
        (
            True,
            {
                "candidates": [
                    {
                        "content": {"parts": [{"inlineData": {}}]},
                        "finishReason": "SAFETY",
                    }
                ]
            },
            "SAFETY",
        ),
        (
            True,
            {
                "promptFeedback": {
                    "blockReason": "SAFETY",
                    "blockReasonMessage": "Blocked",
                }
            },
            "SAFETY",
        ),
    ],
)
async def test_empty_or_blocked_image_response(
    use_adc: bool, response: dict[str, Any], reason: str
) -> None:
    client = GoogleImagesClient(
        model=_model(),
        provider=Provider.GOOGLE,
        auth=GoogleADC(project_id="p") if use_adc else _api_key_auth(),
    )
    with patch.object(
        client._strategy, "_make_request", new=AsyncMock(return_value=response)
    ):
        output = await client.generate("draw")
    assert isinstance(output.content, ImageArtifact)
    assert not output.content.has_content
    assert output.usage is not None and output.usage.num_images == 0
    assert output.finish_reason is not None and output.finish_reason.reason == reason
    if "promptFeedback" in response:
        assert output.finish_reason.message == "Blocked"
        assert (
            output.metadata["raw_response"]["promptFeedback"]
            == response["promptFeedback"]
        )


@pytest.mark.parametrize("use_adc", [False, True])
def test_malformed_image_response_still_raises(use_adc: bool) -> None:
    client = GoogleImagesClient(
        model=_model(),
        provider=Provider.GOOGLE,
        auth=GoogleADC(project_id="p") if use_adc else _api_key_auth(),
    )
    with pytest.raises(ValueError):
        client._parse_content({})


@pytest.mark.parametrize(
    ("arguments", "expected"),
    [
        ([{"queries": ["a", "b"]}], 2),
        ([{"query": "a"}], 1),
        ([{"queries": ["a", "b"], "query": "a"}], 2),
        ([{"queries": []}], 0),
        ([], 0),
        ([{"queries": ["a"]}, {"query": "b"}], 2),
        ([{"queries": ["a"]}, {}], None),
        ([None], None),
        ([{"queries": [""]}], None),
        ([{"queries": "a"}], None),
        ([{"query": " "}], None),
    ],
)
def test_grounding_query_count_omits_unknown_counts(
    arguments: list[dict[str, Any] | None], expected: int | None
) -> None:
    client = GoogleInteractionsImagesClient(
        model=_model(), provider=Provider.GOOGLE, auth=_api_key_auth()
    )
    raw = client._build_metadata(
        {
            "steps": [
                {"type": "google_search_call", "arguments": value}
                for value in arguments
            ]
        }
    )["raw_response"]
    if expected is None:
        assert "grounding_query_count" not in raw
    else:
        assert raw["grounding_query_count"] == expected
    assert "grounding_query_count" not in client._build_metadata({})["raw_response"]
