"""Unit tests for Google audio transcription request building."""

from pydantic import SecretStr

from celeste.artifacts import AudioArtifact
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import AudioMimeType
from celeste.modalities.audio.io import AudioInput
from celeste.modalities.audio.providers.google.client import GoogleAudioClient
from celeste.models import Model


def _client() -> GoogleAudioClient:
    return GoogleAudioClient(
        model=Model(
            id="gemini-3.5-transcribe",
            provider=Provider.GOOGLE,
            display_name="Google Gemini 3.5 Transcribe",
            operations={Modality.AUDIO: {Operation.TRANSCRIBE}},
        ),
        auth=AuthHeader(secret=SecretStr("test")),
        provider=Provider.GOOGLE,
    )


def test_init_request_puts_audio_artifact_as_audio_part() -> None:
    audio = AudioArtifact(data=b"fake-audio", mime_type=AudioMimeType.MP3)
    request = _client()._init_request(AudioInput(audio=audio))
    assert request == {
        "input": [
            {"type": "audio", "data": audio.get_base64(), "mime_type": "audio/mpeg"}
        ],
        "generation_config": {"transcription_config": {}},
    }
