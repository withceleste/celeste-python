"""Unit tests for ElevenLabs audio transcription request building."""

from pydantic import SecretStr

from celeste.artifacts import AudioArtifact
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import AudioMimeType
from celeste.modalities.audio.io import AudioInput
from celeste.modalities.audio.providers.elevenlabs.client import ElevenLabsAudioClient
from celeste.models import Model


def _client() -> ElevenLabsAudioClient:
    return ElevenLabsAudioClient(
        model=Model(
            id="scribe_v2",
            provider=Provider.ELEVENLABS,
            display_name="Scribe v2",
            operations={Modality.AUDIO: {Operation.TRANSCRIBE}},
        ),
        auth=AuthHeader(secret=SecretStr("test"), header="xi-api-key", prefix=""),
        provider=Provider.ELEVENLABS,
    )


def test_init_request_puts_audio_artifact_as_file() -> None:
    audio = AudioArtifact(data=b"fake-audio", mime_type=AudioMimeType.MP3)
    request = _client()._init_request(AudioInput(audio=audio))
    assert request == {"file": audio}


def test_build_request_adds_model_id() -> None:
    audio = AudioArtifact(data=b"fake-audio", mime_type=AudioMimeType.WAV)
    client = _client()
    request = client._build_request(AudioInput(audio=audio), language="en")
    assert request["file"] is audio
    assert request["model_id"] == "scribe_v2"
    assert request["language_code"] == "en"


def test_parse_content_returns_transcript_text() -> None:
    assert _client()._parse_content({"text": "hello world"}) == "hello world"


def test_dispatcher_selects_stt_backend() -> None:
    client = _client()
    assert client._transcribe_endpoint == "/v1/speech-to-text"
    assert client._speak_endpoint is None
