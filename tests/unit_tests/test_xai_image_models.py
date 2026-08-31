"""Registered xAI image models build the dedicated REST request shapes."""

import pytest

from celeste import Modality, create_client
from celeste.artifacts import ImageArtifact
from celeste.exceptions import ConstraintViolationError
from celeste.mime_types import ImageMimeType
from celeste.modalities.images.io import ImageInput
from celeste.modalities.images.providers.xai.client import XAIImagesClient


@pytest.mark.parametrize(
    "model_id",
    ["grok-imagine-image", "grok-imagine-image-quality", "grok-imagine-image-2.0"],
)
def test_registered_xai_models_build_generation_and_ordered_edits(
    model_id: str,
) -> None:
    client = create_client(modality=Modality.IMAGES, model=model_id, api_key="test-key")
    assert isinstance(client, XAIImagesClient)
    image = ImageArtifact(url="https://example.com/primary.png")
    references = [
        ImageArtifact(url="https://example.com/reference.png"),
        ImageArtifact(data=b"reference", mime_type=ImageMimeType.PNG),
    ]

    generated = client._build_request(
        ImageInput(prompt="New image"),
        num_images=2,
        aspect_ratio="21:9",
        resolution="2k",
        output_format="b64_json",
    )
    assert generated == {
        "model": model_id,
        "prompt": "New image",
        "n": 2,
        "aspect_ratio": "21:9",
        "resolution": "2k",
        "response_format": "b64_json",
    }

    edited = client._build_request(
        ImageInput(prompt="Combine", image=image),
        reference_images=references,
        resolution="2k",
    )
    assert edited == {
        "model": model_id,
        "prompt": "Combine",
        "images": [
            {"url": image.url},
            {"url": references[0].url},
            {"url": "data:image/png;base64,cmVmZXJlbmNl"},
        ],
        "resolution": "2k",
    }
    with pytest.raises(ConstraintViolationError):
        client._build_request(
            ImageInput(prompt="Too many sources", image=image),
            reference_images=[image, *references],
        )


def test_generation_quality_uses_the_existing_raw_parameter_path() -> None:
    client = create_client(
        modality=Modality.IMAGES, model="grok-imagine-image-2.0", api_key="test-key"
    )
    assert "quality" not in client.model.supported_parameters
    assert client._build_request(
        ImageInput(prompt="New image"), extra_body={"quality": "low"}
    ) == {
        "model": "grok-imagine-image-2.0",
        "prompt": "New image",
        "quality": "low",
    }
