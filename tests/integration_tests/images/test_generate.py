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
        (Provider.BYTEPLUS, "seedream-4-0-250828", {}),
        (
            Provider.BFL,
            "flux-2-pro",
            {"aspect_ratio": "520x512", "prompt_upsampling": False},
        ),
        (Provider.BFL, "flux-2-klein-4b", {"aspect_ratio": "256x1024"}),
        (Provider.BFL, "flux-kontext-pro", {"aspect_ratio": "4:1"}),
        (Provider.BFL, "flux-pro-1.1-ultra", {"aspect_ratio": "1:1"}),
        (
            Provider.BFL,
            "flux-dev",
            {
                "aspect_ratio": "256x256",
                "steps": 1,
                "guidance": 1.5,
                "output_format": "webp",
            },
        ),
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
