import pytest

from celeste import Modality, Provider, create_client
from celeste.artifacts import ImageArtifact
from celeste.modalities.images import ImageChunk


@pytest.mark.parametrize(
    ("provider", "model"),
    [
        (Provider.OPENAI, "gpt-image-1-mini"),
        (Provider.BYTEPLUS, "seedream-4-0-250828"),
    ],
)
async def test_stream_generate(provider: Provider, model: str) -> None:
    client = create_client(modality=Modality.IMAGES, provider=provider, model=model)

    chunks = [chunk async for chunk in client.stream.generate(prompt="A red apple")]

    assert chunks
    assert all(isinstance(chunk, ImageChunk) for chunk in chunks)
    assert isinstance(chunks[-1].content, ImageArtifact)
    assert chunks[-1].content.has_content
