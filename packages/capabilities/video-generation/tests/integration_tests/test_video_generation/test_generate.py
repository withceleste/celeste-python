"""Integration tests for video generation across all providers."""

import pytest

from celeste import Capability, Provider, create_client


@pytest.mark.parametrize(
    ("provider", "model", "parameters"),
    [
        (
            Provider.OPENAI,
            "sora-2",
            {"duration": "4", "aspect_ratio": "16:9", "resolution": "720p"},
        ),
        (
            Provider.GOOGLE,
            "veo-3.0-fast-generate-001",
            {"duration": 4, "resolution": "720p"},
        ),
        (
            Provider.BYTEDANCE,
            "seedance-1-0-lite-t2v-250428",
            {"duration": 2, "resolution": "480p"},
        ),
    ],
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate(provider: Provider, model: str, parameters: dict) -> None:
    """Test video generation with prompt parameter across all providers.

    This test demonstrates that the unified API works identically across
    all providers using the same code - proving the abstraction value.
    Uses cheapest models with minimum duration and lowest resolution to minimize costs.
    """
    # Import here to avoid circular import during pytest collection
    from celeste_video_generation import (
        VideoGenerationOutput,
        VideoGenerationUsage,
    )

    from celeste.artifacts import VideoArtifact

    # Arrange
    client = create_client(
        capability=Capability.VIDEO_GENERATION,
        provider=provider,
    )
    prompt = "A cinematic video of a sunset over mountains"

    # Act
    response = await client.generate(
        prompt=prompt,
        model=model,
        **parameters,
    )

    # Assert
    assert isinstance(response, VideoGenerationOutput), (
        f"Expected VideoGenerationOutput, got {type(response)}"
    )
    assert isinstance(response.content, VideoArtifact), (
        f"Expected VideoArtifact content, got {type(response.content)}"
    )
    assert response.content.has_content, (
        f"VideoArtifact has no content (url/data/path): {response.content}"
    )

    # Validate usage metrics
    assert isinstance(response.usage, VideoGenerationUsage), (
        f"Expected VideoGenerationUsage, got {type(response.usage)}"
    )
