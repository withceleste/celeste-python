import pytest

from celeste import Modality, Provider, create_client
from celeste.modalities.audio import AudioChunk
from celeste.modalities.audio.parameters import AudioParameter

MODELS = [
    (Provider.ELEVENLABS, "eleven_turbo_v2_5"),
    (Provider.GRADIUM, "default"),
]


@pytest.mark.parametrize(("provider", "model"), MODELS)
async def test_stream_speak(provider: Provider, model: str) -> None:
    client = create_client(modality=Modality.AUDIO, provider=provider, model=model)
    voice = client.model.parameter_constraints[AudioParameter.VOICE].voices[0].name

    chunks = [
        chunk async for chunk in client.stream.speak(text="Hello world", voice=voice)
    ]

    assert chunks
    assert all(isinstance(chunk, AudioChunk) for chunk in chunks)
    assert any(chunk.content.has_content for chunk in chunks)
