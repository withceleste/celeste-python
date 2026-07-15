from typing import Any

import pytest

from celeste import Modality, Provider, create_client
from celeste.artifacts import VideoArtifact
from celeste.modalities.videos import VideoOutput, VideoUsage

pytestmark = pytest.mark.slow


@pytest.mark.parametrize(
    ("provider", "model", "parameters"),
    [
        (Provider.OPENAI, "sora-2", {"duration": 4, "resolution": "720p"}),
        (Provider.GOOGLE, "veo-3.1-fast-generate-preview", {"duration": 4}),
        (
            Provider.BYTEPLUS,
            "seedance-1-0-pro-250528",
            {"duration": 2, "resolution": "480p"},
        ),
        (Provider.XAI, "grok-imagine-video", {"duration": 2}),
    ],
)
async def test_generate(
    provider: Provider, model: str, parameters: dict[str, Any]
) -> None:
    client = create_client(modality=Modality.VIDEOS, provider=provider, model=model)

    response = await client.generate(prompt="A cat walking", **parameters)

    assert isinstance(response, VideoOutput)
    assert isinstance(response.content, VideoArtifact)
    assert response.content.has_content
    assert isinstance(response.usage, VideoUsage)
