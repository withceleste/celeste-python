"""Integration tests for text analyze operation - all audio-capable models."""

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
from celeste.modalities.text import TextOutput, TextUsage  # noqa: E402


@pytest.mark.parametrize(
    "model",
    [
        m
        for m in list_models(modality=Modality.TEXT, operation=Operation.ANALYZE)
        if not m.streaming and InputType.AUDIO in m.optional_input_types
    ],
    ids=lambda m: f"{m.provider.value}-{m.id}",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_analyze_audio(model: Model, test_audio: AudioArtifact) -> None:
    """Test audio analysis for all audio-capable models.

    Dynamically discovers all audio models via list_models() and verifies each
    can analyze audio. Failures indicate deprecated or misconfigured models.
    """
    client = create_client(
        modality=Modality.TEXT,
        model=model,
    )

    response = await client.analyze(
        prompt="Describe what you hear in this audio",
        audio=test_audio,
    )

    assert isinstance(response, TextOutput), (
        f"Expected TextOutput, got {type(response)}"
    )
    # Empty/None content is valid for reasoning models that use all tokens for thinking
    if not response.content:
        assert response.finish_reason is not None, (
            f"Model {model.provider.value}/{model.id} returned empty content without finish_reason"
        )
    assert isinstance(response.usage, TextUsage), (
        f"Expected TextUsage, got {type(response.usage)}"
    )


@pytest.mark.integration
def test_sync_analyze_audio(test_audio: AudioArtifact) -> None:
    """Test sync wrapper works correctly.

    Single model smoke test - sync is just async_to_sync wrapper.
    """
    models = [
        m
        for m in list_models(modality=Modality.TEXT, operation=Operation.ANALYZE)
        if InputType.AUDIO in m.optional_input_types
    ]
    model = models[0]

    client = create_client(
        modality=Modality.TEXT,
        model=model,
    )

    response = client.sync.analyze(
        prompt="Describe what you hear in this audio",
        audio=test_audio,
    )

    assert isinstance(response, TextOutput)
    assert response.content or response.finish_reason is not None
