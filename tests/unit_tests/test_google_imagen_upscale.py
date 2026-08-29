"""Unit tests for Google Imagen 4 upscaling."""

import pytest
from pydantic import SecretStr

from celeste.artifacts import ImageArtifact
from celeste.auth import AuthHeader
from celeste.constraints import Choice
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import ImageMimeType
from celeste.modalities.images.io import ImageInput
from celeste.modalities.images.parameters import ImageParameter
from celeste.modalities.images.providers.google.client import GoogleImagesClient
from celeste.modalities.images.providers.google.imagen import (
    GoogleImagenUpscaleImagesClient,
)
from celeste.modalities.images.providers.google.models import (
    GOOGLE_IMAGEN_MODELS,
    GOOGLE_IMAGEN_UPSCALE_MODELS,
)
from celeste.models import Model
from celeste.providers.google.auth import GoogleADC
from celeste.providers.google.imagen import config


def _model() -> Model:
    return GOOGLE_IMAGEN_UPSCALE_MODELS[0]


def _client(model: Model | None = None) -> GoogleImagesClient:
    return GoogleImagesClient(
        model=model or _model(),
        provider=Provider.GOOGLE,
        auth=GoogleADC(project_id="p", location="us-central1"),
    )


def _api_key_auth() -> AuthHeader:
    return AuthHeader(secret=SecretStr("test"), header="x-goog-api-key", prefix="")


def test_upscale_model_catalog_and_vertex_routing() -> None:
    model = _model()
    factor = model.parameter_constraints[ImageParameter.UPSCALE_FACTOR]

    assert model.id == "imagen-4.0-upscale-preview"
    assert model.operations == {Modality.IMAGES: {Operation.UPSCALE}}
    assert isinstance(factor, Choice)
    assert factor.options == ["x2", "x3", "x4"]

    client = _client()
    assert isinstance(client._strategy, GoogleImagenUpscaleImagesClient)
    assert client._upscale_endpoint == config.GoogleImagenEndpoint.CREATE_IMAGE
    assert client._strategy._build_url(client._upscale_endpoint) == (
        "https://us-central1-aiplatform.googleapis.com/v1/projects/p/locations/"
        "us-central1/publishers/google/models/imagen-4.0-upscale-preview:predict"
    )


def test_upscale_requires_regional_google_adc() -> None:
    with pytest.raises(ValueError, match="GoogleADC"):
        GoogleImagesClient(
            model=_model(), provider=Provider.GOOGLE, auth=_api_key_auth()
        )

    with pytest.raises(ValueError, match="regional"):
        GoogleImagesClient(
            model=_model(),
            provider=Provider.GOOGLE,
            auth=GoogleADC(project_id="p"),
        )


def test_upscale_builds_inline_predict_request() -> None:
    request = _client()._build_request(
        ImageInput(image=ImageArtifact(data=b"abc", mime_type=ImageMimeType.PNG)),
        upscale_factor="x3",
    )

    assert request == {
        "instances": [
            {
                "prompt": "Upscale the image",
                "image": {"bytesBase64Encoded": "YWJj"},
            }
        ],
        "parameters": {
            "mode": "upscale",
            "upscaleConfig": {"upscaleFactor": "x3"},
        },
    }


def test_upscale_builds_gcs_predict_request() -> None:
    request = _client()._build_request(
        ImageInput(image=ImageArtifact(url="gs://bucket/input.jpg")),
        upscale_factor="x2",
    )

    assert request["instances"][0]["image"] == {"gcsUri": "gs://bucket/input.jpg"}


def test_upscale_requires_factor_and_rejects_http_input_url() -> None:
    client = _client()
    with pytest.raises(ValueError, match="upscale_factor"):
        client._build_request(ImageInput(image=ImageArtifact(data=b"abc")))

    with pytest.raises(ValueError, match="gs://"):
        client._build_request(
            ImageInput(image=ImageArtifact(url="https://example.com/input.png")),
            upscale_factor="x2",
        )


@pytest.mark.parametrize(
    "model",
    [*GOOGLE_IMAGEN_MODELS, *GOOGLE_IMAGEN_UPSCALE_MODELS],
    ids=lambda model: model.id,
)
def test_imagen_metadata_retains_only_successful_image_count(model: Model) -> None:
    client = _client(model)
    response_data = {
        "deployedModelId": "served-model",
        "predictions": [
            {"mimeType": "image/png", "bytesBase64Encoded": "YWJj"},
            {"mimeType": "image/jpeg", "bytesBase64Encoded": "ZGVm"},
            {"raiFilteredReason": "Blocked by safety policy."},
        ],
    }

    metadata = client._build_metadata(response_data)

    assert metadata["raw_response"] == {
        "deployedModelId": "served-model",
        "num_images": 2,
    }
    assert client._parse_usage(response_data)["num_images"] == 2

    artifacts = client._parse_content(response_data)
    assert isinstance(artifacts, list)
    assert len(artifacts) == 2
    assert artifacts[0].data == b"abc"
    assert artifacts[1].data == b"def"
