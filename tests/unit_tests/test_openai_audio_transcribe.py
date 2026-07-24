"""Unit tests for OpenAI audio transcription request building."""

from pydantic import SecretStr

from celeste.artifacts import AudioArtifact
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import AudioMimeType
from celeste.modalities.audio.io import AudioInput
from celeste.modalities.audio.providers.openai.client import OpenAIAudioClient
from celeste.models import Model


def _client() -> OpenAIAudioClient:
    return OpenAIAudioClient(
        model=Model(
            id="gpt-4o-mini-transcribe",
            provider=Provider.OPENAI,
            display_name="GPT-4o Mini Transcribe",
            operations={Modality.AUDIO: {Operation.TRANSCRIBE}},
        ),
        auth=AuthHeader(secret=SecretStr("test")),
        provider=Provider.OPENAI,
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
    assert request["model"] == "gpt-4o-mini-transcribe"
    assert request["response_format"] == "json"
    assert request["language"] == "en"


def test_parse_content_returns_transcript_text() -> None:
    assert _client()._parse_content({"text": "hello world"}) == "hello world"


def test_parse_usage_drops_duration_only_usage() -> None:
    assert _client()._parse_usage({"usage": {"type": "duration", "seconds": 2.5}}) == {}


def test_parse_usage_maps_token_usage() -> None:
    assert _client()._parse_usage(
        {
            "usage": {
                "type": "tokens",
                "input_tokens": 10,
                "output_tokens": 20,
                "total_tokens": 30,
            }
        }
    ) == {
        "input_tokens": 10,
        "output_tokens": 20,
        "total_tokens": 30,
    }


def test_build_metadata_promotes_duration_usage() -> None:
    metadata = _client()._build_metadata(
        {
            "text": "hello",
            "language": "en",
            "usage": {"type": "duration", "seconds": 2.5},
        }
    )
    assert metadata["language"] == "en"
    assert metadata["duration"] == 2.5
    assert "text" not in metadata["raw_response"]
