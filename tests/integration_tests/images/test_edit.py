"""Integration tests for images edit operation across providers."""

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
    ("provider", "model"),
    [
        (Provider.OPENAI, "gpt-image-1-mini"),
        (Provider.GOOGLE, "gemini-2.5-flash-image"),
        (Provider.BFL, "flux-2-pro"),
        (Provider.XAI, "grok-imagine-image"),
    ],
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_edit(
    provider: Provider, model: str, square_image: ImageArtifact
) -> None:
    """Test image editing across providers.

    Uses cheapest edit-capable model per provider.
    """
    client = create_client(
        modality=Modality.IMAGES,
        provider=provider,
        model=model,
    )

    response = await client.edit(
        image=square_image,
        prompt="Add a small blue circle in the center",
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
def test_sync_edit(square_image: ImageArtifact) -> None:
    """Test sync edit wrapper works correctly.

    Single model smoke test - sync is just async_to_sync wrapper.
    """
    client = create_client(
        modality=Modality.IMAGES,
        provider=Provider.GOOGLE,
        model="gemini-2.5-flash-image",
    )

    response = client.sync.edit(image=square_image, prompt="Add a red border")

    assert isinstance(response, ImageOutput)
    assert isinstance(response.content, ImageArtifact)
    assert response.content.has_content
