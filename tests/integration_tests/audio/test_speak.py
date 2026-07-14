import pytest

from celeste import Modality, Provider, create_client
from celeste.artifacts import AudioArtifact
from celeste.modalities.audio import AudioOutput
from celeste.modalities.audio.parameters import AudioParameter

MODELS = [
    (Provider.ELEVENLABS, "eleven_v3"),
    (Provider.GOOGLE, "gemini-2.5-flash-tts"),
    (Provider.OPENAI, "tts-1"),
]


@pytest.mark.parametrize(("provider", "model"), MODELS)
async def test_speak(provider: Provider, model: str) -> None:
    client = create_client(modality=Modality.AUDIO, provider=provider, model=model)
    voice = client.model.parameter_constraints[AudioParameter.VOICE].voices[0].name

    response = await client.speak(text="Hello world", voice=voice)

    assert isinstance(response, AudioOutput)
    assert isinstance(response.content, AudioArtifact)
    assert response.content.has_content
