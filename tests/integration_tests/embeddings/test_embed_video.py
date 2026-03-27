"""Integration tests for embeddings embed operation - video inputs."""

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
    create_client,
)
from celeste.artifacts import VideoArtifact  # noqa: E402
from celeste.modalities.embeddings import (  # noqa: E402
    EmbeddingsOutput,
    EmbeddingsUsage,
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_embed_video(test_video: VideoArtifact) -> None:
    """Test embedding a single video."""
    client = create_client(
        modality=Modality.EMBEDDINGS,
        model="gemini-embedding-2-preview",
    )

    response = await client.embed(videos=test_video)

    assert isinstance(response, EmbeddingsOutput)
    assert response.content is not None
    assert isinstance(response.content, list)
    assert len(response.content) > 0
    assert isinstance(response.content[0], float)
    assert isinstance(response.usage, EmbeddingsUsage)


@pytest.mark.integration
def test_sync_embed_video(test_video: VideoArtifact) -> None:
    """Test sync wrapper works correctly.

    Single model smoke test - sync is just async_to_sync wrapper.
    """
    client = create_client(
        modality=Modality.EMBEDDINGS,
        model="gemini-embedding-2-preview",
    )

    response = client.sync.embed(videos=test_video)

    assert isinstance(response, EmbeddingsOutput)
    assert response.content is not None
