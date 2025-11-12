"""Integration tests for image generation across all providers."""

import pytest

from celeste import Capability, Provider, create_client


@pytest.mark.parametrize(
    ("provider", "model", "parameters"),
    [
        (Provider.OPENAI, "dall-e-2", {}),
        (Provider.GOOGLE, "imagen-4.0-fast-generate-001", {}),
        (Provider.BYTEDANCE, "seedream-4-0-250828", {}),
    ],
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate(provider: Provider, model: str, parameters: dict) -> None:
    """Test image generation with prompt parameter across all providers.

    This test demonstrates that the unified API works identically across
    all providers using the same code - proving the abstraction value.
    Uses cheapest models to minimize costs.
    """
    # Import here to avoid circular import during pytest collection
    from celeste_image_generation import (
        ImageGenerationOutput,
        ImageGenerationUsage,
    )

    from celeste.artifacts import ImageArtifact

    # Arrange
    client = create_client(
        capability=Capability.IMAGE_GENERATION,
        provider=provider,
    )
    prompt = "A red apple on a white background"

    # Act
    response = await client.generate(
        prompt=prompt,
        model=model,
        **parameters,
    )

    # Assert
    assert isinstance(response, ImageGenerationOutput), (
        f"Expected ImageGenerationOutput, got {type(response)}"
    )
    assert isinstance(response.content, ImageArtifact), (
        f"Expected ImageArtifact content, got {type(response.content)}"
    )
    assert response.content.has_content, (
        f"ImageArtifact has no content (url/data/path): {response.content}"
    )

    # Validate usage metrics
    assert isinstance(response.usage, ImageGenerationUsage), (
        f"Expected ImageGenerationUsage, got {type(response.usage)}"
    )
