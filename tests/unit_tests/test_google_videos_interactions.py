"""Unit tests for Google videos provider Veo/Interactions dispatch and wire shape."""

import pytest
from pydantic import SecretStr

from celeste import Model
from celeste.artifacts import ImageArtifact, VideoArtifact
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import ImageMimeType, VideoMimeType
from celeste.modalities.videos.io import VideoInput
from celeste.modalities.videos.parameters import VideoParameter
from celeste.modalities.videos.providers.google.client import GoogleVideosClient
from celeste.modalities.videos.providers.google.interactions import (
    GoogleInteractionsVideosClient,
)
from celeste.modalities.videos.providers.google.models import MODELS
from celeste.modalities.videos.providers.google.veo import GoogleVeoVideosClient
from celeste.providers.google.auth import GoogleADC

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


@pytest.mark.parametrize(
    "model_id", ["gemini-omni-1.1-flash", "gemini-omni-1.1-flash-preview"]
)
def test_omni_1_1_models_dispatch_to_interactions_strategy(model_id: str) -> None:
    assert isinstance(_client(model_id)._strategy, GoogleInteractionsVideosClient)


@pytest.mark.parametrize(
    "model_id",
    [
        "veo-3.1-generate-001",
        "veo-3.1-fast-generate-001",
        "veo-3.1-lite-generate-001",
    ],
)
def test_cloud_veo_models_dispatch_to_veo_strategy(model_id: str) -> None:
    assert isinstance(_client(model_id)._strategy, GoogleVeoVideosClient)


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


@pytest.mark.parametrize(
    "model_id", ["gemini-omni-1.1-flash", "gemini-omni-1.1-flash-preview"]
)
def test_omni_1_1_source_video_relies_on_task_inference(model_id: str) -> None:
    request = _client(model_id)._init_request(
        VideoInput(
            prompt="continue the scene",
            video=VideoArtifact(data=b"vid", mime_type=VideoMimeType.MP4),
        )
    )

    assert "generation_config" not in request


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


def test_interactions_high_resolution_uses_developer_uri_delivery() -> None:
    request = _client("gemini-omni-1.1-flash")._build_request(
        VideoInput(prompt="a mountain"), resolution="1080p"
    )

    assert request["response_format"] == {
        "type": "video",
        "resolution": "1080p",
        "delivery": "uri",
    }


def test_cloud_interactions_uses_global_route_body_shape() -> None:
    client = GoogleVideosClient(
        model=_model("gemini-omni-1.1-flash-preview"),
        provider=Provider.GOOGLE,
        auth=GoogleADC(project_id="test-project"),
    )

    request = client._build_request(
        VideoInput(prompt="a mountain"),
        resolution="1080p",
    )

    assert request["response_format"] == [{"type": "video", "resolution": "1080p"}]


def test_veo_edit_maps_video_for_each_auth_surface() -> None:
    direct = _client("veo-3.1-generate-preview")._init_request(
        VideoInput(
            prompt="continue",
            video=VideoArtifact(data=b"vid", mime_type=VideoMimeType.MP4),
        )
    )
    cloud_client = GoogleVideosClient(
        model=_model("veo-3.1-generate-001"),
        provider=Provider.GOOGLE,
        auth=GoogleADC(project_id="test-project"),
    )
    cloud = cloud_client._init_request(
        VideoInput(
            prompt="continue",
            video=VideoArtifact(
                url="gs://bucket/generated.mp4", mime_type=VideoMimeType.MP4
            ),
        )
    )

    assert direct["instances"][0]["video"] == {
        "inlineData": {"data": "dmlk", "mimeType": "video/mp4"}
    }
    assert cloud["instances"][0]["video"] == {
        "gcsUri": "gs://bucket/generated.mp4",
        "mimeType": "video/mp4",
    }


def test_google_video_catalog_capability_matrix() -> None:
    by_id = {model.id: model for model in MODELS}
    references = {
        model_id
        for model_id, model in by_id.items()
        if VideoParameter.REFERENCE_IMAGES in model.supported_parameters
    }
    audio_toggle = {
        model_id
        for model_id, model in by_id.items()
        if VideoParameter.GENERATE_AUDIO in model.supported_parameters
    }

    assert references == {
        "veo-3.1-generate-preview",
        "veo-3.1-fast-generate-preview",
        "veo-3.1-generate-001",
        "veo-3.1-fast-generate-001",
        "gemini-omni-flash-preview",
        "gemini-omni-1.1-flash",
        "gemini-omni-1.1-flash-preview",
    }
    assert audio_toggle == {
        "veo-3.1-generate-001",
        "veo-3.1-fast-generate-001",
        "veo-3.1-lite-generate-001",
    }


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
