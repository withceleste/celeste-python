"""Integration tests for audio speak operation."""

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
from celeste.modalities.audio import AudioOutput, AudioUsage  # noqa: E402


@pytest.mark.parametrize(
    "model",
    [
        m
        for m in list_models(modality=Modality.AUDIO, operation=Operation.SPEAK)
        if not m.streaming  # Streaming models tested in test_stream_speak
    ],
    ids=lambda m: f"{m.provider.value}-{m.id}",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_speak(model: Model) -> None:
    """Test audio speak for all registered non-streaming models.

    Dynamically discovers all models via list_models() and verifies each one
    can speak. Failures indicate deprecated or misconfigured models.
    """
    client = create_client(
        modality=Modality.AUDIO,
        model=model,
    )

    # Get default voice for this model (VoiceConstraint has voices attr)
    voice_constraint = model.parameter_constraints.get("voice")
    voice = voice_constraint.voices[0].name if voice_constraint else None

    response = await client.speak(text="Hello world", voice=voice)

    assert isinstance(response, AudioOutput), (
        f"Expected AudioOutput, got {type(response)}"
    )
    assert isinstance(response.content, AudioArtifact), (
        f"Expected AudioArtifact content, got {type(response.content)}"
    )
    assert response.content.has_content, (
        f"Model {model.provider.value}/{model.id} returned AudioArtifact with no content"
    )
    assert isinstance(response.usage, AudioUsage), (
        f"Expected AudioUsage, got {type(response.usage)}"
    )


@pytest.mark.integration
def test_sync_speak() -> None:
    """Test sync wrapper works correctly.

    Single model smoke test - sync is just async_to_sync wrapper.
    """
    models = [
        m
        for m in list_models(modality=Modality.AUDIO, operation=Operation.SPEAK)
        if not m.streaming
    ]
    model = models[0]

    client = create_client(
        modality=Modality.AUDIO,
        model=model,
    )

    # Get default voice for this model (VoiceConstraint has voices attr)
    voice_constraint = model.parameter_constraints.get("voice")
    voice = voice_constraint.voices[0].name if voice_constraint else None

    response = client.sync.speak(text="Hello", voice=voice)

    assert isinstance(response, AudioOutput)
    assert isinstance(response.content, AudioArtifact)
    assert response.content.has_content
