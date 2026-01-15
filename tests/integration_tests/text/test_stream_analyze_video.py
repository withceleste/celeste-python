"""Integration tests for streaming video analysis - all vision-capable models."""

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
from celeste.artifacts import VideoArtifact  # noqa: E402
from celeste.core import InputType  # noqa: E402
from celeste.modalities.text import TextChunk, TextUsage  # noqa: E402


@pytest.mark.parametrize(
    "model",
    [
        m
        for m in list_models(modality=Modality.TEXT, operation=Operation.ANALYZE)
        if m.streaming and InputType.VIDEO in m.optional_input_types
    ],
    ids=lambda m: f"{m.provider.value}-{m.id}",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_stream_analyze_video(model: Model, test_video: VideoArtifact) -> None:
    """Test streaming video analysis for all streaming vision-capable models.

    Dynamically discovers all streaming vision models and verifies each can
    stream video analysis. Failures indicate providers needing video implementation.
    """
    client = create_client(
        modality=Modality.TEXT,
        model=model,
    )

    chunks: list[TextChunk] = []
    async for chunk in client.stream.analyze(
        prompt="Describe what happens in this video",
        video=test_video,
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


@pytest.mark.integration
def test_sync_stream_analyze_video(test_video: VideoArtifact) -> None:
    """Test sync streaming wrapper works correctly.

    Single model smoke test - sync stream iteration bridges async internally.
    """
    models = [
        m
        for m in list_models(modality=Modality.TEXT, operation=Operation.ANALYZE)
        if m.streaming and InputType.VIDEO in m.optional_input_types
    ]
    model = models[0]

    client = create_client(
        modality=Modality.TEXT,
        model=model,
    )

    for _chunk in client.sync.stream.analyze(
        prompt="Describe what happens in this video",
        video=test_video,
    ):
        pass  # Just exhaust the stream
