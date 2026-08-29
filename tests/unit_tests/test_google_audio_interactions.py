"""Unit tests for Google audio Interactions request and response handling."""

import pytest
from pydantic import SecretStr

from celeste.artifacts import AudioArtifact
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.exceptions import ConstraintViolationError
from celeste.mime_types import AudioMimeType
from celeste.modalities.audio.io import AudioInput
from celeste.modalities.audio.providers.google.client import GoogleAudioClient
from celeste.modalities.audio.providers.google.models import MODELS


def _client(model_id: str) -> GoogleAudioClient:
    model = next(model for model in MODELS if model.id == model_id)
    return GoogleAudioClient(
        model=model,
        auth=AuthHeader(secret=SecretStr("test"), header="x-goog-api-key", prefix=""),
        provider=Provider.GOOGLE,
    )


def test_google_audio_catalog_streaming_and_transcription_flags() -> None:
    models = {model.id: model for model in MODELS}

    assert not models["gemini-2.5-flash-preview-tts"].streaming
    assert not models["gemini-2.5-pro-preview-tts"].streaming
    assert models["gemini-3.1-flash-tts-preview"].streaming
    assert models["gemini-3.5-transcribe"].operations == {
        Modality.AUDIO: {Operation.TRANSCRIBE}
    }


def test_transcribe_request_maps_audio_and_language_hint() -> None:
    audio = AudioArtifact(
        data=b"pcm",
        mime_type=AudioMimeType.PCM,
        metadata={"sample_rate": 16000, "channels": 1},
    )

    request = _client("gemini-3.5-transcribe")._build_request(
        AudioInput(audio=audio), language="en"
    )

    assert request == {
        "input": [
            {
                "type": "audio",
                "data": "cGNt",
                "mime_type": "audio/l16",
                "sample_rate": 16000,
                "channels": 1,
            }
        ],
        "generation_config": {"transcription_config": {"language_codes": ["en-US"]}},
        "model": "gemini-3.5-transcribe",
    }


def test_transcribe_request_accepts_a_single_audio_artifact_list() -> None:
    audio = AudioArtifact(data=b"audio", mime_type=AudioMimeType.OPUS)

    request = _client("gemini-3.5-transcribe")._build_request(AudioInput(audio=[audio]))

    assert request["input"] == [
        {"type": "audio", "data": "YXVkaW8=", "mime_type": "audio/opus"}
    ]


def test_transcribe_request_rejects_multiple_audio_artifacts() -> None:
    audio = AudioArtifact(data=b"audio", mime_type=AudioMimeType.MP3)

    with pytest.raises(ValueError, match="requires exactly one AudioArtifact"):
        _client("gemini-3.5-transcribe")._init_request(AudioInput(audio=[audio, audio]))


def test_transcribe_request_rejects_unsupported_audio_format() -> None:
    audio = AudioArtifact(data=b"audio", mime_type=AudioMimeType.WMA)

    with pytest.raises(ConstraintViolationError, match="mime_type must be one of"):
        _client("gemini-3.5-transcribe")._init_request(AudioInput(audio=audio))


def test_transcribe_parses_all_text_and_preserves_usage_and_annotations() -> None:
    annotation = {
        "type": "word_info",
        "text": "Hello",
        "speaker": "spk_1",
        "start_offset": "0.100s",
        "end_offset": "0.450s",
    }
    text_blocks = [
        {"type": "text", "text": "Hello ", "annotations": [annotation]},
        {"type": "text", "text": "world"},
    ]
    response = {
        "id": "interactions/abc",
        "status": "completed",
        "steps": [{"type": "model_output", "content": text_blocks}],
        "usage": {
            "total_input_tokens": 10,
            "total_output_tokens": 2,
            "total_tokens": 12,
        },
    }
    client = _client("gemini-3.5-transcribe")

    assert client._parse_content(response) == "Hello world"
    assert client._parse_usage(response) == {
        "input_tokens": 10,
        "output_tokens": 2,
        "total_tokens": 12,
        "reasoning_tokens": None,
        "cached_tokens": None,
    }
    metadata = client._build_metadata(response)
    assert metadata["annotations"] == [annotation]
    assert "text_blocks" not in metadata
    assert metadata["raw_response"]["usage"] == response["usage"]
    assert "steps" not in metadata["raw_response"]


def test_lyria_uses_final_audio_and_preserves_ordered_text_blocks() -> None:
    response = {
        "status": "completed",
        "steps": [
            {
                "type": "model_output",
                "content": [
                    {"type": "text", "text": "[Verse]\nFirst line"},
                    {"type": "audio", "data": "Zmlyc3Q=", "mime_type": "audio/mp3"},
                    {"type": "text", "text": '{"structure":["verse","chorus"]}'},
                ],
            },
            {
                "type": "model_output",
                "content": [
                    {
                        "type": "audio",
                        "data": "ZmluYWw=",
                        "mime_type": "audio/mp3",
                        "sample_rate": 44100,
                        "channels": 2,
                    }
                ],
            },
        ],
    }
    client = _client("lyria-3-clip-preview")

    artifact = client._parse_content(response)

    assert isinstance(artifact, AudioArtifact)
    assert artifact.data == b"final"
    assert artifact.mime_type == AudioMimeType.MP3
    assert artifact.metadata == {"sample_rate": 44100, "channels": 2}
    assert client._build_metadata(response)["text_blocks"] == [
        {"type": "text", "text": "[Verse]\nFirst line"},
        {"type": "text", "text": '{"structure":["verse","chorus"]}'},
    ]
