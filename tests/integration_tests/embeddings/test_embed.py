"""Integration tests for embeddings embed operation."""

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
from celeste.modalities.embeddings import (  # noqa: E402
    EmbeddingsOutput,
    EmbeddingsUsage,
)


@pytest.mark.parametrize(
    "model",
    [m for m in list_models(modality=Modality.EMBEDDINGS, operation=Operation.EMBED)],
    ids=lambda m: f"{m.provider.value}-{m.id}",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_embed_single(model: Model) -> None:
    """Test embeddings for single text input."""
    client = create_client(
        modality=Modality.EMBEDDINGS,
        model=model,
    )

    response = await client.embed("Hello world")

    assert isinstance(response, EmbeddingsOutput), (
        f"Expected EmbeddingsOutput, got {type(response)}"
    )
    assert response.content is not None, (
        f"Model {model.provider.value}/{model.id} returned None content"
    )
    # Single text input should return list[float]
    assert isinstance(response.content, list), "Content should be a list"
    assert len(response.content) > 0, "Embedding vector should not be empty"
    assert isinstance(response.content[0], float), (
        "Single text should return list[float], not list[list[float]]"
    )
    assert isinstance(response.usage, EmbeddingsUsage), (
        f"Expected EmbeddingsUsage, got {type(response.usage)}"
    )


@pytest.mark.parametrize(
    "model",
    [m for m in list_models(modality=Modality.EMBEDDINGS, operation=Operation.EMBED)],
    ids=lambda m: f"{m.provider.value}-{m.id}",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_embed_batch(model: Model) -> None:
    """Test embeddings for batch text input."""
    client = create_client(
        modality=Modality.EMBEDDINGS,
        model=model,
    )

    response = await client.embed(["Hello", "World"])

    assert isinstance(response, EmbeddingsOutput), (
        f"Expected EmbeddingsOutput, got {type(response)}"
    )
    assert response.content is not None, (
        f"Model {model.provider.value}/{model.id} returned None content"
    )
    # Batch text input should return list[list[float]]
    assert isinstance(response.content, list), "Content should be a list"
    assert len(response.content) == 2, "Should have 2 embeddings for 2 inputs"
    assert isinstance(response.content[0], list), (
        "Batch text should return list[list[float]]"
    )
    assert isinstance(response.content[0][0], float), (
        "Each embedding should be list[float]"
    )


@pytest.mark.integration
def test_sync_embed() -> None:
    """Test sync wrapper works correctly."""
    models = list_models(modality=Modality.EMBEDDINGS, operation=Operation.EMBED)
    model = models[0]

    client = create_client(
        modality=Modality.EMBEDDINGS,
        model=model,
    )

    response = client.sync.embed("Hello")

    assert isinstance(response, EmbeddingsOutput)
    assert response.content is not None
