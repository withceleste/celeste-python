"""Integration tests for videos generate operation across all providers."""

import warnings

# Suppress deprecation warnings from legacy capability packages
warnings.filterwarnings(
    "ignore",
    message=".*capability parameter is deprecated.*",
    category=DeprecationWarning,
)

import pytest  # noqa: E402

from celeste import Modality, Provider, create_client  # noqa: E402
from celeste.artifacts import VideoArtifact  # noqa: E402
from celeste.modalities.videos import VideoOutput, VideoUsage  # noqa: E402


@pytest.mark.parametrize(
    ("provider", "model", "parameters"),
    [
        # OpenAI Sora: min duration 4s, only 720p available
        (Provider.OPENAI, "sora-2", {"duration": 4, "resolution": "720p"}),
        # Google Veo: duration options [4, 6, 8], 720p available
        (Provider.GOOGLE, "veo-3.0-fast-generate-001", {"duration": 4}),
        # BytePlus Seedance: min duration 2s, 480p is cheapest
        (
            Provider.BYTEPLUS,
            "seedance-1-0-lite-t2v-250428",
            {"duration": 2, "resolution": "480p"},
        ),
        # xAI Grok Imagine: duration 1-15s, 480p/720p
        (Provider.XAI, "grok-imagine-video", {"duration": 2}),
    ],
)
@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.asyncio
async def test_generate(provider: Provider, model: str, parameters: dict) -> None:
    """Test video generation across providers.

    Uses cheapest/fastest model per provider with minimum duration/resolution
    to minimize costs. Marked as slow since video generation takes 30-120+ seconds.
    """
    client = create_client(
        modality=Modality.VIDEOS,
        provider=provider,
        model=model,
    )

    response = await client.generate(
        prompt="A cat walking on the beach",
        **parameters,
    )

    assert isinstance(response, VideoOutput), (
        f"Expected VideoOutput, got {type(response)}"
    )
    assert isinstance(response.content, VideoArtifact), (
        f"Expected VideoArtifact content, got {type(response.content)}"
    )
    assert response.content.has_content, (
        f"VideoArtifact has no content (url/data/path): {response.content}"
    )
    assert isinstance(response.usage, VideoUsage), (
        f"Expected VideoUsage, got {type(response.usage)}"
    )


@pytest.mark.integration
@pytest.mark.slow
def test_sync_generate() -> None:
    """Test sync wrapper works correctly.

    Single model smoke test - sync is just async_to_sync wrapper.
    Uses BytePlus Seedance with minimum settings (cheapest option).
    """
    client = create_client(
        modality=Modality.VIDEOS,
        provider=Provider.BYTEPLUS,
        model="seedance-1-0-lite-t2v-250428",
    )

    response = client.sync.generate(
        prompt="A ball rolling",
        duration=2,
        resolution="480p",
    )

    assert isinstance(response, VideoOutput)
    assert isinstance(response.content, VideoArtifact)
    assert response.content.has_content
