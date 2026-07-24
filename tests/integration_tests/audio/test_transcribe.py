"""Integration tests for audio transcription."""

import pytest

from celeste import Modality, Operation, Provider, create_client
from celeste.artifacts import AudioArtifact
from celeste.modalities.text.io import TextOutput

MODELS = [
    (Provider.GROQ, "whisper-large-v3-turbo"),
    (Provider.GROQ, "whisper-large-v3"),
]


@pytest.mark.parametrize(("provider", "model"), MODELS)
async def test_transcribe(
    provider: Provider, model: str, test_audio: AudioArtifact
) -> None:
    client = create_client(
        modality=Modality.AUDIO,
        operation=Operation.TRANSCRIBE,
        provider=provider,
        model=model,
    )

    response = await client.transcribe(test_audio)

    assert isinstance(response, TextOutput)
    assert isinstance(response.content, str)
    assert response.content.strip()
