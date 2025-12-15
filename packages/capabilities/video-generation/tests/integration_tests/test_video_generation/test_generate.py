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
            Provider.BYTEPLUS,
            "seedance-1-0-lite-t2v-250428",
            {"duration": 2, "resolution": "480p"},
        ),
    ],
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate(provider: Provider, model: str, parameters: dict) -> None:
    """Test video generation across all providers. Uses cheapest models."""
    # Import inside function to avoid circular import
    from celeste_video_generation import VideoGenerationOutput, VideoGenerationUsage

    from celeste.artifacts import VideoArtifact

    # Arrange
    client = create_client(
        capability=Capability.VIDEO_GENERATION,
        provider=provider,
        model=model,
    )
    prompt = "A cat playing with a ball"

    # Act
    response = await client.generate(
        prompt=prompt,
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
