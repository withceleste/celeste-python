"""Tests for the existing Google Imagen generation path."""

from celeste.artifacts import ImageArtifact
from celeste.core import Provider
from celeste.modalities.images.providers.google.client import GoogleImagesClient
from celeste.modalities.images.providers.google.models import GOOGLE_IMAGEN_MODELS
from celeste.providers.google.auth import GoogleADC


def test_imagen_retains_only_successful_image_count() -> None:
    client = GoogleImagesClient(
        model=GOOGLE_IMAGEN_MODELS[0],
        provider=Provider.GOOGLE,
        auth=GoogleADC(project_id="p", location="us-central1"),
    )
    response = {
        "deployedModelId": "served-model",
        "predictions": [
            {"mimeType": "image/png", "bytesBase64Encoded": "YWJj"},
            {"raiFilteredReason": "Blocked by safety policy."},
        ],
    }

    assert client._build_metadata(response)["raw_response"] == {
        "deployedModelId": "served-model",
        "num_images": 1,
    }
    assert client._parse_usage(response)["num_images"] == 1
    content = client._parse_content(response)
    assert isinstance(content, ImageArtifact)
    assert content.data == b"abc"
