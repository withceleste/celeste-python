import pytest

from celeste import Modality, Provider, create_client
from celeste.artifacts import ImageArtifact
from celeste.modalities.embeddings import EmbeddingsOutput
from celeste.providers.google.auth import GoogleADC

MODEL = "gemini-embedding-2-preview"


@pytest.mark.parametrize(
    ("field", "fixture"),
    [("audio", "test_audio"), ("images", "square_image"), ("videos", "test_video")],
)
async def test_embed_media(
    field: str, fixture: str, request: pytest.FixtureRequest
) -> None:
    client = create_client(
        modality=Modality.EMBEDDINGS, provider=Provider.GOOGLE, model=MODEL
    )

    response = await client.embed(**{field: request.getfixturevalue(fixture)})

    assert isinstance(response, EmbeddingsOutput)
    assert response.content
    assert isinstance(response.content[0], float)


async def test_embed_batch_images(square_image: ImageArtifact) -> None:
    client = create_client(
        modality=Modality.EMBEDDINGS, provider=Provider.GOOGLE, model=MODEL
    )

    response = await client.embed(images=[square_image, square_image])

    assert isinstance(response, EmbeddingsOutput)
    assert len(response.content) == 2
    first = response.content[0]
    assert isinstance(first, list)
    assert first
    assert isinstance(first[0], float)


async def test_embed_text_and_image(square_image: ImageArtifact) -> None:
    client = create_client(
        modality=Modality.EMBEDDINGS, provider=Provider.GOOGLE, model=MODEL
    )

    response = await client.embed(text="a square", images=square_image)

    assert isinstance(response, EmbeddingsOutput)
    assert response.content
    assert isinstance(response.content[0], float)


async def test_vertex_rejects_multimodal(square_image: ImageArtifact) -> None:
    client = create_client(
        modality=Modality.EMBEDDINGS,
        provider=Provider.GOOGLE,
        model=MODEL,
        auth=GoogleADC(),
    )

    with pytest.raises(ValueError, match="not yet supported via Vertex AI"):
        await client.embed(images=square_image)
