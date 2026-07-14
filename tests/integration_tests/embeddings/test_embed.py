import pytest

from celeste import Modality, Provider, create_client
from celeste.modalities.embeddings import EmbeddingsOutput
from celeste.providers.google.auth import GoogleADC

MODEL = "gemini-embedding-001"


@pytest.mark.parametrize(
    ("value", "expected_count"),
    [("Hello world", None), (["Hello", "World"], 2)],
)
async def test_embed(value: str | list[str], expected_count: int | None) -> None:
    client = create_client(
        modality=Modality.EMBEDDINGS, provider=Provider.GOOGLE, model=MODEL
    )

    response = await client.embed(value)

    assert isinstance(response, EmbeddingsOutput)
    assert response.content
    if expected_count is None:
        assert isinstance(response.content[0], float)
    else:
        assert len(response.content) == expected_count
        first = response.content[0]
        assert isinstance(first, list)
        assert first
        assert isinstance(first[0], float)


async def test_vertex_embed() -> None:
    client = create_client(
        modality=Modality.EMBEDDINGS,
        provider=Provider.GOOGLE,
        model=MODEL,
        auth=GoogleADC(),
    )

    response = await client.embed("Hello world")

    assert isinstance(response, EmbeddingsOutput)
    assert response.content
    assert isinstance(response.content[0], float)
