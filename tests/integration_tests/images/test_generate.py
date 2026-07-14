from typing import Any

import pytest

from celeste import Modality, Provider, create_client
from celeste.artifacts import ImageArtifact
from celeste.modalities.images import ImageOutput, ImageUsage
from celeste.providers.google.auth import GoogleADC


@pytest.mark.parametrize(
    ("provider", "model", "parameters"),
    [
        (Provider.OPENAI, "gpt-image-1-mini", {}),
        (Provider.GOOGLE, "imagen-4.0-fast-generate-001", {"num_images": 1}),
        (Provider.BYTEPLUS, "seedream-4-0-250828", {}),
        (Provider.BFL, "flux-2-pro", {}),
        (Provider.XAI, "grok-imagine-image", {}),
    ],
)
async def test_generate(
    provider: Provider, model: str, parameters: dict[str, Any]
) -> None:
    client = create_client(modality=Modality.IMAGES, provider=provider, model=model)

    response = await client.generate(prompt="A red apple", **parameters)

    assert isinstance(response, ImageOutput)
    assert isinstance(response.content, ImageArtifact)
    assert response.content.has_content
    assert isinstance(response.usage, ImageUsage)


@pytest.mark.parametrize(
    ("model", "parameters"),
    [
        ("imagen-4.0-fast-generate-001", {"num_images": 1}),
        ("gemini-2.5-flash-image", {}),
    ],
)
async def test_vertex_generate(model: str, parameters: dict[str, Any]) -> None:
    client = create_client(
        modality=Modality.IMAGES,
        provider=Provider.GOOGLE,
        model=model,
        auth=GoogleADC(),
    )

    response = await client.generate(prompt="A red apple", **parameters)

    assert isinstance(response, ImageOutput)
    assert isinstance(response.content, ImageArtifact)
    assert response.content.has_content
