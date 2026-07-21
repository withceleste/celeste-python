"""Unit tests for Google videos provider Veo/Interactions dispatch and wire shape."""

import pytest
from pydantic import SecretStr

from celeste import Model
from celeste.artifacts import ImageArtifact, VideoArtifact
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import ImageMimeType, VideoMimeType
from celeste.modalities.videos.io import VideoInput
from celeste.modalities.videos.providers.google.client import GoogleVideosClient
from celeste.modalities.videos.providers.google.interactions import (
    GoogleInteractionsVideosClient,
)
from celeste.modalities.videos.providers.google.veo import GoogleVeoVideosClient

IMAGE = ImageArtifact(data=b"img", mime_type=ImageMimeType.PNG)


def _model(model_id: str) -> Model:
    return Model(
        id=model_id,
        provider=Provider.GOOGLE,
        display_name=model_id,
        operations={Modality.VIDEOS: {Operation.GENERATE, Operation.EDIT}},
    )


def _client(model_id: str) -> GoogleVideosClient:
    return GoogleVideosClient(
        model=_model(model_id),
        provider=Provider.GOOGLE,
        auth=AuthHeader(secret=SecretStr("test"), header="x-goog-api-key", prefix=""),
    )


def test_veo_model_dispatches_to_veo_strategy() -> None:
    client = _client("veo-3.1-generate-preview")
    assert isinstance(client._strategy, GoogleVeoVideosClient)
    assert client._generate_endpoint == client._strategy._generate_endpoint
    assert client._edit_endpoint == client._strategy._edit_endpoint


def test_omni_model_dispatches_to_interactions_strategy() -> None:
    client = _client("gemini-omni-flash-preview")
    assert isinstance(client._strategy, GoogleInteractionsVideosClient)
    assert client._generate_endpoint == client._strategy._generate_endpoint
    assert client._edit_endpoint == client._strategy._edit_endpoint


def test_unknown_model_raises() -> None:
    with pytest.raises(ValueError, match="Unknown Google videos model"):
        _client("veo-99-unknown")


def test_interactions_init_request_generate_is_string_input() -> None:
    client = _client("gemini-omni-flash-preview")

    request = client._init_request(VideoInput(prompt="a rolling marble"))

    assert request == {
        "input": "a rolling marble",
        "response_format": {"type": "video"},
    }


def test_interactions_init_request_edit_sends_video_part_and_task() -> None:
    client = _client("gemini-omni-flash-preview")

    request = client._init_request(
        VideoInput(
            prompt="make the mirror ripple",
            video=VideoArtifact(data=b"vid", mime_type=VideoMimeType.MP4),
        )
    )

    assert request["input"] == [
        {"type": "video", "data": "dmlk", "mime_type": "video/mp4"},
        {"type": "text", "text": "make the mirror ripple"},
    ]
    assert request["generation_config"] == {"video_config": {"task": "edit"}}
    assert request["response_format"] == {"type": "video"}


def test_interactions_build_request_first_and_last_frame() -> None:
    client = _client("gemini-omni-flash-preview")

    request = client._build_request(
        VideoInput(prompt="animate this"),
        first_frame=IMAGE,
        last_frame=IMAGE,
        aspect_ratio="9:16",
    )

    parts = request["input"]
    assert [p["type"] for p in parts] == ["image", "image", "text"]
    assert parts[-1] == {"type": "text", "text": "animate this"}
    assert request["generation_config"]["video_config"]["task"] == "image_to_video"
    assert request["response_format"]["aspect_ratio"] == "9:16"


def test_interactions_build_request_reference_images() -> None:
    client = _client("gemini-omni-flash-preview")

    request = client._build_request(
        VideoInput(prompt="a cat with yarn"),
        reference_images=[IMAGE, IMAGE],
    )

    parts = request["input"]
    assert [p["type"] for p in parts] == ["image", "image", "text"]
    assert request["generation_config"]["video_config"]["task"] == "reference_to_video"


@pytest.mark.parametrize(
    ("part", "data", "url"),
    [
        ({"type": "video", "mime_type": "video/mp4", "data": "dmlk"}, b"vid", None),
        (
            {"type": "video", "mime_type": "video/mp4", "uri": "https://f/x"},
            None,
            "https://f/x",
        ),
    ],
)
def test_interactions_parse_content_video_variants(
    part: dict, data: bytes | None, url: str | None
) -> None:
    client = GoogleInteractionsVideosClient(
        model=_model("gemini-omni-flash-preview"),
        provider=Provider.GOOGLE,
        auth=AuthHeader(secret=SecretStr("test"), header="x-goog-api-key", prefix=""),
    )

    artifact = client._parse_content(
        {"status": "completed", "steps": [{"type": "model_output", "content": [part]}]}
    )

    assert isinstance(artifact, VideoArtifact)
    assert artifact.data == data
    assert artifact.url == url
    assert artifact.mime_type == VideoMimeType.MP4


def test_dispatcher_forwards_download_content() -> None:
    client = _client("gemini-omni-flash-preview")
    assert "download_content" in type(client).__dict__
