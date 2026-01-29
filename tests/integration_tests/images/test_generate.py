"""Integration tests for images generate operation across all providers."""

import warnings

# Suppress deprecation warnings from legacy capability packages
warnings.filterwarnings(
    "ignore",
    message=".*capability parameter is deprecated.*",
    category=DeprecationWarning,
)

import pytest  # noqa: E402

from celeste import Modality, Provider, create_client  # noqa: E402
from celeste.artifacts import ImageArtifact  # noqa: E402
from celeste.modalities.images import ImageOutput, ImageUsage  # noqa: E402


@pytest.mark.parametrize(
    ("provider", "model", "parameters"),
    [
        (Provider.OPENAI, "dall-e-2", {}),
        (Provider.GOOGLE, "imagen-4.0-fast-generate-001", {"num_images": 1}),
        (Provider.BYTEPLUS, "seedream-4-0-250828", {}),
        (Provider.BFL, "flux-2-pro", {}),
        (Provider.XAI, "grok-imagine-image", {}),
    ],
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate(provider: Provider, model: str, parameters: dict) -> None:
    """Test image generation across providers.

    Uses cheapest model per provider to minimize costs.
    """
    client = create_client(
        modality=Modality.IMAGES,
        provider=provider,
        model=model,
    )

    response = await client.generate(
        prompt="A red apple on a white background",
        **parameters,
    )

    assert isinstance(response, ImageOutput), (
        f"Expected ImageOutput, got {type(response)}"
    )
    assert isinstance(response.content, ImageArtifact), (
        f"Expected ImageArtifact content, got {type(response.content)}"
    )
    assert response.content.has_content, (
        f"ImageArtifact has no content (url/data/path): {response.content}"
    )
    assert isinstance(response.usage, ImageUsage), (
        f"Expected ImageUsage, got {type(response.usage)}"
    )


@pytest.mark.integration
def test_sync_generate() -> None:
    """Test sync wrapper works correctly.

    Single model smoke test - sync is just async_to_sync wrapper.
    """
    client = create_client(
        modality=Modality.IMAGES,
        provider=Provider.GOOGLE,
        model="imagen-4.0-fast-generate-001",
    )

    response = client.sync.generate(prompt="A red circle", num_images=1)

    assert isinstance(response, ImageOutput)
    # Content may be list or single artifact depending on provider
    content = (
        response.content[0] if isinstance(response.content, list) else response.content
    )
    assert isinstance(content, ImageArtifact)
    assert content.has_content
