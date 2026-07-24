"""Unit tests for Groq audio transcription request building."""

from pydantic import SecretStr

from celeste.artifacts import AudioArtifact
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import AudioMimeType
from celeste.modalities.audio.io import AudioInput
from celeste.modalities.audio.providers.groq.client import GroqAudioClient
from celeste.models import Model


def _client() -> GroqAudioClient:
    return GroqAudioClient(
        model=Model(
            id="whisper-large-v3-turbo",
            provider=Provider.GROQ,
            display_name="Whisper Large V3 Turbo",
            operations={Modality.AUDIO: {Operation.TRANSCRIBE}},
        ),
        auth=AuthHeader(secret=SecretStr("test")),
        provider=Provider.GROQ,
    )


def test_init_request_puts_audio_artifact_as_file() -> None:
    audio = AudioArtifact(data=b"fake-audio", mime_type=AudioMimeType.MP3)
    request = _client()._init_request(AudioInput(audio=audio))
    assert request == {"file": audio}


def test_build_request_adds_model_and_default_response_format() -> None:
    audio = AudioArtifact(data=b"fake-audio", mime_type=AudioMimeType.WAV)
    client = _client()
    request = client._build_request(AudioInput(audio=audio), language="en")
    assert request["file"] is audio
    assert request["model"] == "whisper-large-v3-turbo"
    assert request["response_format"] == "json"
    assert request["language"] == "en"


def test_parse_content_returns_transcript_text() -> None:
    assert _client()._parse_content({"text": "hello world"}) == "hello world"
