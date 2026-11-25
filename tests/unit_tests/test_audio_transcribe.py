"""Unit tests for audio transcription request building."""

from typing import Any

import pytest
from pydantic import SecretStr

from celeste.artifacts import AudioArtifact
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import AudioMimeType
from celeste.modalities.audio.io import AudioInput
from celeste.modalities.audio.providers.elevenlabs.client import ElevenLabsAudioClient
from celeste.modalities.audio.providers.groq.client import GroqAudioClient
from celeste.modalities.audio.providers.mistral.client import MistralAudioClient
from celeste.modalities.audio.providers.openai.client import OpenAIAudioClient
from celeste.models import Model

type _Transcriber = (
    ElevenLabsAudioClient | GroqAudioClient | MistralAudioClient | OpenAIAudioClient
)

# Provider -> (client class, model id, auth header, request fields beyond the file).
_CLIENTS: dict[Provider, tuple[type[_Transcriber], str, AuthHeader, dict[str, Any]]] = {
    Provider.ELEVENLABS: (
        ElevenLabsAudioClient,
        "scribe_v2",
        AuthHeader(secret=SecretStr("test"), header="xi-api-key", prefix=""),
        {"model_id": "scribe_v2", "language_code": "en"},
    ),
    Provider.GROQ: (
        GroqAudioClient,
        "whisper-large-v3-turbo",
        AuthHeader(secret=SecretStr("test")),
        {
            "model": "whisper-large-v3-turbo",
            "response_format": "json",
            "language": "en",
        },
    ),
    Provider.MISTRAL: (
        MistralAudioClient,
        "voxtral-mini-latest",
        AuthHeader(secret=SecretStr("test")),
        {"model": "voxtral-mini-latest", "language": "en"},
    ),
    Provider.OPENAI: (
        OpenAIAudioClient,
        "gpt-4o-mini-transcribe",
        AuthHeader(secret=SecretStr("test")),
        {
            "model": "gpt-4o-mini-transcribe",
            "response_format": "json",
            "language": "en",
        },
    ),
}


def _client(provider: Provider) -> _Transcriber:
    client_cls, model_id, auth, _ = _CLIENTS[provider]
    return client_cls(
        model=Model(
            id=model_id,
            provider=provider,
            display_name=model_id,
            operations={Modality.AUDIO: {Operation.TRANSCRIBE}},
        ),
        auth=auth,
        provider=provider,
    )


@pytest.mark.parametrize("provider", list(_CLIENTS))
def test_transcription_request_and_transcript_text(provider: Provider) -> None:
    audio = AudioArtifact(data=b"fake-audio", mime_type=AudioMimeType.WAV)
    client = _client(provider)

    assert client._init_request(AudioInput(audio=audio)) == {"file": audio}
    request = client._build_request(AudioInput(audio=audio), language="en")
    assert request["file"] is audio
    assert request == {"file": audio, **_CLIENTS[provider][3]}
    assert client._parse_content({"text": "hello world"}) == "hello world"


def test_elevenlabs_dispatcher_selects_stt_backend() -> None:
    client = _client(Provider.ELEVENLABS)
    assert client._transcribe_endpoint == "/v1/speech-to-text"
    assert client._speak_endpoint is None


def test_openai_parse_usage_drops_duration_only_usage() -> None:
    usage = {"usage": {"type": "duration", "seconds": 2.5}}
    assert _client(Provider.OPENAI)._parse_usage(usage) == {}


def test_openai_parse_usage_maps_token_usage() -> None:
    tokens = {"input_tokens": 10, "output_tokens": 20, "total_tokens": 30}
    usage = {"usage": {"type": "tokens", **tokens}}
    assert _client(Provider.OPENAI)._parse_usage(usage) == tokens


def test_openai_build_metadata_promotes_duration_usage() -> None:
    metadata = _client(Provider.OPENAI)._build_metadata(
        {
            "text": "hello",
            "language": "en",
            "usage": {"type": "duration", "seconds": 2.5},
        }
    )
    assert metadata["language"] == "en"
    assert metadata["duration"] == 2.5
    assert "text" not in metadata["raw_response"]
