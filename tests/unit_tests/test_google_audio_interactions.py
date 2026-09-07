import base64
from secrets import token_hex

import pytest

from celeste import Modality, Operation, Provider, create_client
from celeste.artifacts import ImageArtifact
from celeste.auth import AuthHeader
from celeste.exceptions import ConstraintViolationError
from celeste.mime_types import AudioMimeType, ImageMimeType
from celeste.modalities.audio.io import AudioInput
from celeste.models import list_models


def test_lyria_family_and_image_request_contract() -> None:
    models = list_models(
        provider=Provider.GOOGLE, modality=Modality.AUDIO, operation=Operation.GENERATE
    )
    assert {model.id for model in models} == {
        "lyria-3-clip-preview",
        "lyria-3-pro-preview",
        "lyria-3.5",
    }
    images = [ImageArtifact(data=b"image", mime_type=ImageMimeType.PNG)] * 10
    for model in models:
        client = create_client(
            modality=Modality.AUDIO,
            model=model.id,
            auth=AuthHeader(secret=token_hex(8)),
        )
        request = client._build_request(
            AudioInput(text="Music"), reference_images=images
        )
        assert request["model"] == model.id
        assert request["response_format"] == {"type": "audio"}
        assert request["input"][0] == {"type": "text", "text": "Music"}
        assert len(request["input"]) == 11
        assert all(part["type"] == "image" for part in request["input"][1:])
        with pytest.raises(ConstraintViolationError):
            client._build_request(
                AudioInput(text="Music"), reference_images=images + images[:1]
            )


@pytest.mark.parametrize(
    "model",
    [
        "lyria-3.5",
        "gemini-2.5-flash-preview-tts",
        "gemini-2.5-pro-preview-tts",
        "gemini-3.1-flash-tts-preview",
    ],
)
def test_final_audio_and_ordered_text_preserve_usage(model: str) -> None:
    client = create_client(
        modality=Modality.AUDIO, model=model, auth=AuthHeader(secret=token_hex(8))
    )
    first = {"type": "audio", "data": base64.b64encode(b"draft").decode()}
    final = {
        "type": "audio",
        "data": base64.b64encode(b"final").decode(),
        "mime_type": "audio/mpeg",
        "sample_rate": 44100,
        "channels": 2,
    }
    texts = [{"type": "text", "text": "Verse"}, {"type": "text", "text": "Chorus"}]
    response = {
        "id": "song-1",
        "usage": {"total_output_tokens": 305},
        "steps": [
            {"type": "model_output", "content": [texts[0], first]},
            {"type": "model_output", "content": [texts[1], final]},
            {"type": "tool_result", "content": [first]},
        ],
    }
    artifact = client._parse_content(response)
    assert artifact.data == b"final"
    assert artifact.mime_type == AudioMimeType.MP3
    assert artifact.metadata == {"sample_rate": 44100, "channels": 2}
    metadata = client._build_metadata(response)
    assert metadata["text_blocks"] == texts
    assert metadata["raw_response"]["usage"] == response["usage"]
    assert "steps" not in metadata["raw_response"]
    response["steps"] = [{"type": "model_output", "content": [final]}]
    assert client._parse_content(response) == artifact
    assert "text_blocks" not in client._build_metadata(response)
    response["steps"] = [{"type": "model_output", "content": texts}]
    with pytest.raises(ValueError, match="No audio content"):
        client._parse_content(response)
