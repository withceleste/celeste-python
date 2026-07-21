import pytest

from celeste import Modality, Provider, create_client
from celeste.artifacts import VideoArtifact
from celeste.modalities.videos import VideoOutput

pytestmark = pytest.mark.slow

MODELS = [
    (Provider.GOOGLE, "gemini-omni-flash-preview"),
]


@pytest.mark.parametrize(("provider", "model"), MODELS)
async def test_edit(provider: Provider, model: str) -> None:
    client = create_client(modality=Modality.VIDEOS, provider=provider, model=model)

    generated = await client.generate(prompt="A red ball bouncing on a white floor")
    source = await client.download_content(generated.content)

    response = await client.edit(video=source, prompt="Make the ball blue")

    assert isinstance(response, VideoOutput)
    assert isinstance(response.content, VideoArtifact)
    assert response.content.has_content
