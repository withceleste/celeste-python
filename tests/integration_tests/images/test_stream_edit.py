from celeste import Modality, Provider, create_client
from celeste.artifacts import ImageArtifact
from celeste.modalities.images import ImageChunk


async def test_stream_edit(square_image: ImageArtifact) -> None:
    client = create_client(
        modality=Modality.IMAGES,
        provider=Provider.OPENAI,
        model="gpt-image-1-mini",
    )

    chunks = [
        chunk
        async for chunk in client.stream.edit(
            image=square_image, prompt="Add a blue circle"
        )
    ]

    assert chunks
    assert all(isinstance(chunk, ImageChunk) for chunk in chunks)
    assert isinstance(chunks[-1].content, ImageArtifact)
    assert chunks[-1].content.has_content
