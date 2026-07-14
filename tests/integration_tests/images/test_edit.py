import pytest

from celeste import Modality, Provider, create_client
from celeste.artifacts import ImageArtifact
from celeste.modalities.images import ImageOutput, ImageUsage


@pytest.mark.parametrize(
    ("provider", "model"),
    [
        (Provider.OPENAI, "gpt-image-1-mini"),
        (Provider.GOOGLE, "gemini-2.5-flash-image"),
        (Provider.BFL, "flux-2-pro"),
        (Provider.XAI, "grok-imagine-image"),
    ],
)
async def test_edit(
    provider: Provider, model: str, square_image: ImageArtifact
) -> None:
    client = create_client(modality=Modality.IMAGES, provider=provider, model=model)

    response = await client.edit(image=square_image, prompt="Add a blue circle")

    assert isinstance(response, ImageOutput)
    assert isinstance(response.content, ImageArtifact)
    assert response.content.has_content
    assert isinstance(response.usage, ImageUsage)
