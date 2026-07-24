"""Unit tests for Mistral audio transcription request building."""

from pydantic import SecretStr

from celeste.artifacts import AudioArtifact
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import AudioMimeType
from celeste.modalities.audio.io import AudioInput
from celeste.modalities.audio.providers.mistral.client import MistralAudioClient
from celeste.models import Model


def _client() -> MistralAudioClient:
    return MistralAudioClient(
        model=Model(
            id="voxtral-mini-latest",
            provider=Provider.MISTRAL,
            display_name="Voxtral Mini Transcribe (Latest)",
            operations={Modality.AUDIO: {Operation.TRANSCRIBE}},
        ),
        auth=AuthHeader(secret=SecretStr("test")),
        provider=Provider.MISTRAL,
    )


def test_init_request_puts_audio_artifact_as_file() -> None:
    audio = AudioArtifact(data=b"fake-audio", mime_type=AudioMimeType.MP3)
    request = _client()._init_request(AudioInput(audio=audio))
    assert request == {"file": audio}


def test_build_request_adds_model() -> None:
    audio = AudioArtifact(data=b"fake-audio", mime_type=AudioMimeType.WAV)
    client = _client()
    request = client._build_request(AudioInput(audio=audio), language="en")
    assert request["file"] is audio
    assert request["model"] == "voxtral-mini-latest"
    assert request["language"] == "en"


def test_parse_content_returns_transcript_text() -> None:
    assert _client()._parse_content({"text": "hello world"}) == "hello world"
