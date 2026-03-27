"""Integration tests for embeddings embed operation - audio inputs."""

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
from celeste.artifacts import AudioArtifact  # noqa: E402
from celeste.core import InputType  # noqa: E402
from celeste.modalities.embeddings import (  # noqa: E402
    EmbeddingsOutput,
    EmbeddingsUsage,
)


@pytest.mark.parametrize(
    "model",
    [
        m
        for m in list_models(modality=Modality.EMBEDDINGS, operation=Operation.EMBED)
        if InputType.AUDIO in m.optional_input_types
    ],
    ids=lambda m: f"{m.provider}-{m.id}",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_embed_audio(model: Model, test_audio: AudioArtifact) -> None:
    """Test embedding a single audio file."""
    client = create_client(
        modality=Modality.EMBEDDINGS,
        model=model,
    )

    response = await client.embed(audio=test_audio)

    assert isinstance(response, EmbeddingsOutput)
    assert response.content is not None
    assert isinstance(response.content, list)
    assert len(response.content) > 0
    assert isinstance(response.content[0], float)
    assert isinstance(response.usage, EmbeddingsUsage)


@pytest.mark.integration
def test_sync_embed_audio(test_audio: AudioArtifact) -> None:
    """Test sync wrapper works correctly.

    Single model smoke test - sync is just async_to_sync wrapper.
    """
    models = [
        m
        for m in list_models(modality=Modality.EMBEDDINGS, operation=Operation.EMBED)
        if InputType.AUDIO in m.optional_input_types
    ]
    model = models[0]

    client = create_client(
        modality=Modality.EMBEDDINGS,
        model=model,
    )

    response = client.sync.embed(audio=test_audio)

    assert isinstance(response, EmbeddingsOutput)
    assert response.content is not None
