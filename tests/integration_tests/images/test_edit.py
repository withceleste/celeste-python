from typing import Any

import pytest

from celeste import Modality, Provider, create_client
from celeste.artifacts import ImageArtifact
from celeste.modalities.images import ImageOutput, ImageUsage


@pytest.mark.parametrize(
    ("provider", "model", "parameters", "reference_count"),
    [
        (Provider.OPENAI, "gpt-image-1-mini", {}, 0),
        (Provider.GOOGLE, "gemini-2.5-flash-image", {}, 0),
        (Provider.BFL, "flux-2-pro", {"aspect_ratio": "512x512"}, 7),
        (Provider.BFL, "flux-2-klein-4b", {"aspect_ratio": "512x512"}, 4),
        (Provider.BFL, "flux-kontext-pro", {"aspect_ratio": "1:1"}, 3),
        (Provider.XAI, "grok-imagine-image", {}, 0),
    ],
)
async def test_edit(
    provider: Provider,
    model: str,
    parameters: dict[str, Any],
    reference_count: int,
    square_image: ImageArtifact,
) -> None:
    client = create_client(modality=Modality.IMAGES, provider=provider, model=model)

    if reference_count:
        parameters = {
            **parameters,
            "reference_images": [square_image] * reference_count,
        }
    response = await client.edit(
        image=square_image, prompt="Add a blue circle", **parameters
    )

    assert isinstance(response, ImageOutput)
    assert isinstance(response.content, ImageArtifact)
    assert response.content.has_content
    assert isinstance(response.usage, ImageUsage)
