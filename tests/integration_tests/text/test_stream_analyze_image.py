"""Integration tests for streaming image analysis - all vision-capable models."""

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
from celeste.modalities.text import TextChunk, TextUsage  # noqa: E402

TEST_MAX_TOKENS = 200


@pytest.mark.parametrize(
    "model",
    [
        m
        for m in list_models(modality=Modality.TEXT, operation=Operation.ANALYZE)
        if m.streaming and InputType.IMAGE in m.optional_input_types
    ],
    ids=lambda m: f"{m.provider.value}-{m.id}",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_stream_analyze(model: Model, square_image: ImageArtifact) -> None:
    """Test streaming image analysis for all streaming vision-capable models.

    Dynamically discovers all streaming vision models and verifies each can
    stream analysis. Failures indicate deprecated or misconfigured models.
    """
    client = create_client(
        modality=Modality.TEXT,
        model=model,
    )

    chunks: list[TextChunk] = []
    async for chunk in client.stream.analyze(
        prompt="What is this?",
        image=square_image,
        max_tokens=TEST_MAX_TOKENS,
    ):
        chunks.append(chunk)

    # Assert - empty stream is valid for reasoning models that use all tokens for thinking
    if not chunks:
        return

    # Assert - received chunks are valid
    assert all(isinstance(c, TextChunk) for c in chunks), (
        "All chunks should be TextChunk"
    )
    # Assert - content accumulated
    content = "".join(c.content or "" for c in chunks)
    # Empty/None content is valid for reasoning models that use all tokens for thinking
    if not content:
        usage_chunks = [c for c in chunks if c.usage is not None]
        assert usage_chunks, (
            f"Model {model.provider.value}/{model.id} returned empty content without usage"
        )

    # Assert - usage in final chunks (provider-dependent)
    usage_chunks = [c for c in chunks if c.usage is not None]
    if usage_chunks:
        usage = usage_chunks[-1].usage
        assert isinstance(usage, TextUsage), f"Expected TextUsage, got {type(usage)}"
        if usage.output_tokens is not None and usage.output_tokens > TEST_MAX_TOKENS:
            warnings.warn(
                f"Model {model.provider.value}/{model.id} exceeded max_tokens: {usage.output_tokens} > {TEST_MAX_TOKENS}",
                stacklevel=1,
            )


@pytest.mark.integration
def test_sync_stream_analyze(square_image: ImageArtifact) -> None:
    """Test sync streaming wrapper works correctly.

    Single model smoke test - sync stream iteration bridges async internally.
    """
    models = [
        m
        for m in list_models(modality=Modality.TEXT, operation=Operation.ANALYZE)
        if m.streaming and InputType.IMAGE in m.optional_input_types
    ]
    model = models[0]

    client = create_client(
        modality=Modality.TEXT,
        model=model,
    )

    for _chunk in client.sync.stream.analyze(
        prompt="What is this?",
        image=square_image,
        max_tokens=TEST_MAX_TOKENS,
    ):
        pass  # Just exhaust the stream
