"""Unit tests for Google images provider Interactions/Vertex dispatch and wire shape."""

import pytest
from pydantic import SecretStr

from celeste import Model
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


def _model(model_id: str = "gemini-3.1-flash-image") -> Model:
    return Model(
        id=model_id,
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


@pytest.mark.parametrize(
    "model_id",
    [
        "gemini-3-pro-image",
        "gemini-3.1-flash-image",
        "gemini-3.1-flash-lite-image",
    ],
)
def test_vertex_global_only_image_models_reject_regional_adc(model_id: str) -> None:
    with pytest.raises(ValueError, match="only available in the global"):
        GoogleImagesClient(
            model=_model(model_id),
            provider=Provider.GOOGLE,
            auth=GoogleADC(project_id="p", location="us-central1"),
        )

    client = GoogleImagesClient(
        model=_model(model_id),
        provider=Provider.GOOGLE,
        auth=GoogleADC(project_id="p"),
    )
    assert isinstance(client._strategy, GoogleVertexImagesClient)


def test_vertex_2_5_flash_image_allows_regional_adc() -> None:
    client = GoogleImagesClient(
        model=_model("gemini-2.5-flash-image"),
        provider=Provider.GOOGLE,
        auth=GoogleADC(project_id="p", location="us-central1"),
    )

    assert isinstance(client._strategy, GoogleVertexImagesClient)
    assert client._strategy._build_url(client._edit_endpoint).startswith(
        "https://us-central1-aiplatform.googleapis.com/"
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


def test_vertex_parses_and_counts_final_inline_image_parts() -> None:
    client = GoogleVertexImagesClient(
        model=_model(),
        provider=Provider.GOOGLE,
        auth=GoogleADC(project_id="p"),
    )
    response_data = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"inlineData": {"data": "YWJj", "mimeType": "image/png"}},
                        {
                            "thought": True,
                            "inlineData": {
                                "data": "dGhvdWdodA==",
                                "mimeType": "image/png",
                            },
                        },
                        {"text": "Between images"},
                        {
                            "inlineData": {
                                "data": "ZGVm",
                                "mimeType": "image/jpeg",
                            }
                        },
                    ]
                }
            },
            {"finishReason": "SAFETY"},
        ]
    }

    assert client._parse_usage(response_data)["num_images"] == 2

    artifacts = client._parse_content(response_data)

    assert isinstance(artifacts, list)
    assert len(artifacts) == 2
    assert artifacts[0].data == b"abc"
    assert artifacts[0].mime_type == ImageMimeType.PNG
    assert artifacts[1].data == b"def"
    assert artifacts[1].mime_type == ImageMimeType.JPEG


def test_vertex_prompt_feedback_without_candidates_returns_empty_artifact() -> None:
    client = GoogleVertexImagesClient(
        model=_model(),
        provider=Provider.GOOGLE,
        auth=GoogleADC(project_id="p"),
    )
    response_data = {
        "promptFeedback": {
            "blockReason": "SAFETY",
            "blockReasonMessage": "The prompt was blocked for safety.",
            "safetyRatings": [{"category": "HARM_CATEGORY_DANGEROUS_CONTENT"}],
        }
    }

    artifact = client._parse_content(response_data)

    assert isinstance(artifact, ImageArtifact)
    assert not artifact.has_content
    assert client._parse_usage(response_data)["num_images"] == 0
    finish_reason = client._parse_finish_reason(response_data)
    assert finish_reason.reason == "SAFETY"
    assert finish_reason.message == "The prompt was blocked for safety."
    assert client._build_metadata(response_data)["raw_response"] == response_data


def test_vertex_metadata_retains_only_grounding_query_counts() -> None:
    client = GoogleVertexImagesClient(
        model=_model(),
        provider=Provider.GOOGLE,
        auth=GoogleADC(project_id="p"),
    )
    response_data = {
        "responseId": "response-id",
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "inlineData": {
                                "data": "c2Vuc2l0aXZl",
                                "mimeType": "image/png",
                            }
                        }
                    ]
                },
                "groundingMetadata": {
                    "webSearchQueries": ["first query", "second query"],
                    "imageSearchQueries": ["image query"],
                    "groundingChunks": [{"web": {"uri": "https://example.com"}}],
                },
            }
        ],
        "usageMetadata": {"promptTokenCount": 5},
    }

    metadata = client._build_metadata(response_data)

    assert metadata["raw_response"] == {
        "responseId": "response-id",
        "usageMetadata": {"promptTokenCount": 5},
        "grounding_web_query_count": 2,
        "grounding_image_query_count": 1,
    }


def test_interactions_parses_and_counts_inline_and_uri_images() -> None:
    client = GoogleInteractionsImagesClient(
        model=_model(), provider=Provider.GOOGLE, auth=_api_key_auth()
    )
    response_data = {
        "status": "completed",
        "steps": [
            {
                "type": "model_output",
                "content": [
                    {
                        "type": "image",
                        "data": "YWJj",
                        "mime_type": "image/png",
                    },
                    {"type": "text", "text": "Between images"},
                    {
                        "type": "image",
                        "uri": "https://example.com/generated.jpg",
                    },
                    {"type": "image"},
                ],
            }
        ],
    }

    assert client._parse_usage(response_data)["num_images"] == 2

    artifacts = client._parse_content(response_data)

    assert isinstance(artifacts, list)
    assert len(artifacts) == 2
    assert artifacts[0].data == b"abc"
    assert artifacts[0].url is None
    assert artifacts[0].mime_type == ImageMimeType.PNG
    assert artifacts[1].data is None
    assert artifacts[1].url == "https://example.com/generated.jpg"
    assert artifacts[1].mime_type is None


def test_interactions_metadata_retains_only_executed_search_count() -> None:
    client = GoogleInteractionsImagesClient(
        model=_model(), provider=Provider.GOOGLE, auth=_api_key_auth()
    )
    response_data = {
        "id": "interaction-id",
        "usage": {"total_tokens": 10},
        "steps": [
            {
                "type": "google_search_call",
                "arguments": {"queries": ["web query", "image query"]},
                "result": {"sensitive": "provider payload"},
            },
            {
                "type": "google_search_call",
                "arguments": {"queries": ["second image query"]},
            },
            {
                "type": "model_output",
                "content": [
                    {
                        "type": "image",
                        "data": "c2Vuc2l0aXZl",
                        "mime_type": "image/png",
                    }
                ],
            },
        ],
    }

    metadata = client._build_metadata(response_data)

    assert metadata["raw_response"] == {
        "id": "interaction-id",
        "usage": {"total_tokens": 10},
        "grounding_query_count": 3,
    }


def test_interactions_metadata_emits_query_count_only_when_steps_are_present() -> None:
    client = GoogleInteractionsImagesClient(
        model=_model(), provider=Provider.GOOGLE, auth=_api_key_auth()
    )
    usage = {"grounding_tool_count": [{"type": "google_search", "count": 2}]}

    omitted_steps = client._build_metadata({"usage": usage})
    empty_steps = client._build_metadata({"usage": usage, "steps": []})

    assert omitted_steps["raw_response"] == {"usage": usage}
    assert empty_steps["raw_response"] == {
        "usage": usage,
        "grounding_query_count": 0,
    }
