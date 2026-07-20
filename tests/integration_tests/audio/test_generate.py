import pytest

from celeste import Modality, Provider, create_client
from celeste.artifacts import AudioArtifact, ImageArtifact
from celeste.modalities.audio import AudioOutput

MODELS = [
    (Provider.GOOGLE, "lyria-3-clip-preview"),
]


@pytest.mark.parametrize(("provider", "model"), MODELS)
async def test_generate(provider: Provider, model: str) -> None:
    client = create_client(modality=Modality.AUDIO, provider=provider, model=model)

    response = await client.generate(
        prompt="A short instrumental acoustic guitar piece."
    )

    assert isinstance(response, AudioOutput)
    assert isinstance(response.content, AudioArtifact)
    assert response.content.has_content


@pytest.mark.parametrize(("provider", "model"), MODELS)
async def test_generate_with_reference_images(
    provider: Provider, model: str, square_image: ImageArtifact
) -> None:
    client = create_client(modality=Modality.AUDIO, provider=provider, model=model)

    response = await client.generate(
        prompt="An ambient track inspired by the mood and colors in this image.",
        reference_images=[square_image],
    )

    assert isinstance(response, AudioOutput)
    assert isinstance(response.content, AudioArtifact)
    assert response.content.has_content
