"""OpenAI speech formats preserve their wire encoding and artifact MIME type."""

from typing import Any

import pytest
from pydantic import SecretStr

from celeste.artifacts import AudioArtifact
from celeste.auth import AuthHeader
from celeste.constraints import ConstraintViolationError
from celeste.mime_types import AudioMimeType
from celeste.modalities.audio.io import AudioInput
from celeste.modalities.audio.providers.openai.client import OpenAIAudioClient
from celeste.modalities.audio.providers.openai.models import MODELS


def _client(model_id: str = "tts-1") -> OpenAIAudioClient:
    return OpenAIAudioClient(
        model=next(model for model in MODELS if model.id == model_id),
        auth=AuthHeader(secret=SecretStr("test")),
    )


@pytest.mark.parametrize(
    "model_id",
    ["tts-1", "tts-1-hd", "gpt-4o-mini-tts", "gpt-4o-mini-tts-2025-12-15"],
)
@pytest.mark.parametrize(
    ("wire", "mime_type"),
    [
        ("mp3", AudioMimeType.MP3),
        ("opus", AudioMimeType.OGG),
        ("aac", AudioMimeType.AAC),
        ("flac", AudioMimeType.FLAC),
        ("wav", AudioMimeType.WAV),
    ],
)
def test_speech_format_round_trips(
    model_id: str, wire: str, mime_type: AudioMimeType
) -> None:
    client = _client(model_id)
    content = AudioArtifact(data=b"speech", metadata={"marker": "preserved"})
    for value in (wire, wire.upper(), mime_type, mime_type.value):
        request = client._build_request(
            AudioInput(text="Hello"), voice="alloy", output_format=value
        )
        output = client._transform_output(content, output_format=value)
        assert request["response_format"] == wire
        assert isinstance(output, AudioArtifact)
        assert output.mime_type == mime_type
        assert output.data == content.data
        assert output.metadata == content.metadata


@pytest.mark.parametrize(
    ("response_data", "mime_type"),
    [
        (
            {
                "headers": {"content-type": "audio/ogg; codecs=opus"},
                "response_format": "wav",
            },
            AudioMimeType.OGG,
        ),
        (
            {
                "headers": {"content-type": "application/octet-stream"},
                "response_format": "wav",
            },
            AudioMimeType.WAV,
        ),
        ({"response_format": "pcm"}, AudioMimeType.PCM),
        ({"response_format": "mp3"}, AudioMimeType.MP3),
    ],
)
def test_speech_response_preserves_applied_format(
    response_data: dict[str, Any], mime_type: AudioMimeType
) -> None:
    client = _client()
    response_data = {"audio_bytes": b"speech", **response_data}
    content = client._parse_content(response_data)
    output = client._transform_output(content, output_format="audio/aac")
    assert isinstance(output, AudioArtifact)
    assert output.data == b"speech"
    assert output.mime_type == mime_type
    assert "audio_bytes" not in client._build_metadata(response_data)["raw_response"]


def test_speech_format_override_uses_existing_request_escape_hatch() -> None:
    client = _client()
    request = client._build_request(
        AudioInput(text="Hello"),
        voice="alloy",
        output_format="aac",
        extra_body={"response_format": "wav"},
    )
    assert request["response_format"] == "wav"

    with pytest.raises(ConstraintViolationError):
        client._build_request(AudioInput(text="Hello"), output_format="pcm")
