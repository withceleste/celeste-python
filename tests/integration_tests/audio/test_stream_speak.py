"""Integration tests for streaming audio speak."""

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
from celeste.modalities.audio import AudioChunk, AudioUsage  # noqa: E402


@pytest.mark.parametrize(
    "model",
    [
        m
        for m in list_models(modality=Modality.AUDIO, operation=Operation.SPEAK)
        if m.streaming
    ],
    ids=lambda m: f"{m.provider.value}-{m.id}",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_stream_speak(model: Model) -> None:
    """Test streaming audio speak for all streaming-capable models.

    Dynamically discovers all streaming models and verifies each can stream.
    Failures indicate deprecated or misconfigured models.
    """
    client = create_client(
        modality=Modality.AUDIO,
        model=model,
    )

    # Get default voice for this model (VoiceConstraint has voices attr)
    voice_constraint = model.parameter_constraints.get("voice")
    voice = voice_constraint.voices[0].name if voice_constraint else None

    chunks: list[AudioChunk] = []
    async for chunk in client.stream.speak(text="Hello world", voice=voice):
        chunks.append(chunk)

    # Assert - received at least one chunk
    assert chunks, f"Model {model.provider.value}/{model.id} returned no chunks"

    # Assert - all chunks are valid type
    assert all(isinstance(c, AudioChunk) for c in chunks), (
        "All chunks should be AudioChunk"
    )

    # Assert - usage in final chunks (provider-dependent)
    usage_chunks = [c for c in chunks if c.usage is not None]
    if usage_chunks:
        usage = usage_chunks[-1].usage
        assert isinstance(usage, AudioUsage), f"Expected AudioUsage, got {type(usage)}"


@pytest.mark.integration
def test_sync_stream_speak() -> None:
    """Test sync streaming wrapper works correctly.

    Single model smoke test - sync stream iteration bridges async internally.
    """
    models = [
        m
        for m in list_models(modality=Modality.AUDIO, operation=Operation.SPEAK)
        if m.streaming
    ]
    model = models[0]

    client = create_client(
        modality=Modality.AUDIO,
        model=model,
    )

    # Get default voice for this model (VoiceConstraint has voices attr)
    voice_constraint = model.parameter_constraints.get("voice")
    voice = voice_constraint.voices[0].name if voice_constraint else None

    for _chunk in client.sync.stream.speak(text="Hello", voice=voice):
        pass  # Just exhaust the stream
