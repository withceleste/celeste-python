"""Integration tests for streaming image generation across providers."""

import warnings

# Suppress deprecation warnings from legacy capability packages
warnings.filterwarnings(
    "ignore",
    message=".*capability parameter is deprecated.*",
    category=DeprecationWarning,
)

import pytest  # noqa: E402

from celeste import Modality, Provider, create_client  # noqa: E402
from celeste.artifacts import ImageArtifact  # noqa: E402
from celeste.modalities.images import ImageChunk, ImageUsage  # noqa: E402


@pytest.mark.parametrize(
    ("provider", "model"),
    [
        (Provider.OPENAI, "gpt-image-1-mini"),
        (Provider.BYTEPLUS, "seedream-4-0-250828"),
    ],
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_stream_generate(provider: Provider, model: str) -> None:
    """Test streaming image generation across providers.

    Uses cheapest streaming-capable model per provider.
    """
    client = create_client(
        modality=Modality.IMAGES,
        provider=provider,
        model=model,
    )

    chunks: list[ImageChunk] = []
    async for chunk in client.stream.generate(
        prompt="A red apple on a white background"
    ):
        chunks.append(chunk)

    assert len(chunks) > 0, "Expected at least one chunk"
    assert all(isinstance(c, ImageChunk) for c in chunks), (
        "All chunks should be ImageChunk"
    )

    final_chunk = chunks[-1]
    assert isinstance(final_chunk.content, ImageArtifact), (
        f"Expected ImageArtifact, got {type(final_chunk.content)}"
    )
    assert final_chunk.content.has_content, (
        f"Final chunk ImageArtifact has no content: {final_chunk.content}"
    )

    usage_chunks = [c for c in chunks if c.usage is not None]
    if usage_chunks:
        assert isinstance(usage_chunks[-1].usage, ImageUsage), (
            f"Expected ImageUsage, got {type(usage_chunks[-1].usage)}"
        )


@pytest.mark.integration
def test_sync_stream_generate() -> None:
    """Test sync streaming wrapper works correctly.

    Single model smoke test - sync stream iteration bridges async internally.
    """
    from celeste import Model, Operation, list_models

    models = [
        m
        for m in list_models(modality=Modality.IMAGES, operation=Operation.GENERATE)
        if m.streaming
    ]
    model: Model = models[0]

    client = create_client(
        modality=Modality.IMAGES,
        model=model,
    )

    for _chunk in client.sync.stream.generate(
        prompt="A red apple on a white background"
    ):
        pass  # Just exhaust the stream
