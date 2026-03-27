"""Integration tests for embeddings embed operation - image inputs."""

import warnings

# Suppress deprecation warnings from legacy capability packages
warnings.filterwarnings(
    "ignore",
    message=".*capability parameter is deprecated.*",
    category=DeprecationWarning,
)

import pytest  # noqa: E402

from celeste import (  # noqa: E402
    Modality,
    Model,
    Operation,
    create_client,
    list_models,
)
from celeste.artifacts import ImageArtifact  # noqa: E402
from celeste.core import InputType  # noqa: E402
from celeste.modalities.embeddings import (  # noqa: E402
    EmbeddingsOutput,
    EmbeddingsUsage,
)
from celeste.providers.google.auth import GoogleADC  # noqa: E402


@pytest.mark.parametrize(
    "model",
    [
        m
        for m in list_models(modality=Modality.EMBEDDINGS, operation=Operation.EMBED)
        if InputType.IMAGE in m.optional_input_types
    ],
    ids=lambda m: f"{m.provider}-{m.id}",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_embed_image(model: Model, square_image: ImageArtifact) -> None:
    """Test embedding a single image."""
    client = create_client(
        modality=Modality.EMBEDDINGS,
        model=model,
    )

    response = await client.embed(images=square_image)

    assert isinstance(response, EmbeddingsOutput)
    assert response.content is not None
    assert isinstance(response.content, list)
    assert len(response.content) > 0
    assert isinstance(response.content[0], float)
    assert isinstance(response.usage, EmbeddingsUsage)


@pytest.mark.parametrize(
    "model",
    [
        m
        for m in list_models(modality=Modality.EMBEDDINGS, operation=Operation.EMBED)
        if InputType.IMAGE in m.optional_input_types
    ],
    ids=lambda m: f"{m.provider}-{m.id}",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_embed_batch_images(model: Model, square_image: ImageArtifact) -> None:
    """Test embedding multiple images returns separate vectors."""
    client = create_client(
        modality=Modality.EMBEDDINGS,
        model=model,
    )

    response = await client.embed(images=[square_image, square_image])

    assert isinstance(response, EmbeddingsOutput)
    assert isinstance(response.content, list)
    assert len(response.content) == 2
    assert isinstance(response.content[0], list)
    assert isinstance(response.content[0][0], float)


@pytest.mark.parametrize(
    "model",
    [
        m
        for m in list_models(modality=Modality.EMBEDDINGS, operation=Operation.EMBED)
        if InputType.IMAGE in m.optional_input_types
    ],
    ids=lambda m: f"{m.provider}-{m.id}",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_embed_text_and_image(model: Model, square_image: ImageArtifact) -> None:
    """Test aggregated text+image embedding produces a single vector."""
    client = create_client(
        modality=Modality.EMBEDDINGS,
        model=model,
    )

    response = await client.embed(text="a square shape", images=square_image)

    assert isinstance(response, EmbeddingsOutput)
    assert isinstance(response.content, list)
    assert len(response.content) > 0
    assert isinstance(response.content[0], float)


@pytest.mark.integration
def test_sync_embed_image(square_image: ImageArtifact) -> None:
    """Test sync wrapper works correctly.

    Single model smoke test - sync is just async_to_sync wrapper.
    """
    models = [
        m
        for m in list_models(modality=Modality.EMBEDDINGS, operation=Operation.EMBED)
        if InputType.IMAGE in m.optional_input_types
    ]
    model = models[0]

    client = create_client(
        modality=Modality.EMBEDDINGS,
        model=model,
    )

    response = client.sync.embed(images=square_image)

    assert isinstance(response, EmbeddingsOutput)
    assert response.content is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_vertex_embed_image_raises(square_image: ImageArtifact) -> None:
    """Test that multimodal + Vertex AI raises a clear error."""
    client = create_client(
        modality=Modality.EMBEDDINGS,
        provider="google",
        model="gemini-embedding-2-preview",
        auth=GoogleADC(),
    )

    with pytest.raises(ValueError, match="not yet supported via Vertex AI"):
        await client.embed(images=square_image)
