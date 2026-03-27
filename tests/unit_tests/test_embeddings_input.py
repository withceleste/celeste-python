"""Unit tests for EmbeddingsInput validation."""

import pytest

from celeste.artifacts import AudioArtifact, ImageArtifact, VideoArtifact
from celeste.mime_types import AudioMimeType, ImageMimeType, VideoMimeType
from celeste.modalities.embeddings.io import EmbeddingsInput

_TEST_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
    b"\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00"
    b"\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)


def test_text_only() -> None:
    inp = EmbeddingsInput(text="hello")
    assert inp.text == "hello"
    assert inp.images is None
    assert inp.videos is None


def test_batch_text() -> None:
    inp = EmbeddingsInput(text=["a", "b"])
    assert isinstance(inp.text, list)


def test_image_only() -> None:
    img = ImageArtifact(data=_TEST_PNG_BYTES, mime_type=ImageMimeType.PNG)
    inp = EmbeddingsInput(images=img)
    assert inp.images is not None
    assert inp.text is None


def test_image_list() -> None:
    img1 = ImageArtifact(data=_TEST_PNG_BYTES, mime_type=ImageMimeType.PNG)
    img2 = ImageArtifact(data=_TEST_PNG_BYTES, mime_type=ImageMimeType.PNG)
    inp = EmbeddingsInput(images=[img1, img2])
    assert isinstance(inp.images, list)
    assert len(inp.images) == 2


def test_video_only() -> None:
    vid = VideoArtifact(data=b"\x00" * 10, mime_type=VideoMimeType.MP4)
    inp = EmbeddingsInput(videos=vid)
    assert inp.videos is not None


def test_text_and_image() -> None:
    img = ImageArtifact(data=_TEST_PNG_BYTES, mime_type=ImageMimeType.PNG)
    inp = EmbeddingsInput(text="a cat", images=img)
    assert inp.text == "a cat"
    assert inp.images is not None


def test_no_input_raises() -> None:
    with pytest.raises(Exception, match="At least one"):
        EmbeddingsInput()


def test_batch_text_with_image_raises() -> None:
    img = ImageArtifact(data=_TEST_PNG_BYTES, mime_type=ImageMimeType.PNG)
    with pytest.raises(Exception, match="Batch text"):
        EmbeddingsInput(text=["a", "b"], images=img)


def test_batch_text_with_video_raises() -> None:
    vid = VideoArtifact(data=b"\x00" * 10, mime_type=VideoMimeType.MP4)
    with pytest.raises(Exception, match="Batch text"):
        EmbeddingsInput(text=["a", "b"], videos=vid)


def test_audio_only() -> None:
    aud = AudioArtifact(data=b"\x00" * 10, mime_type=AudioMimeType.MP3)
    inp = EmbeddingsInput(audio=aud)
    assert inp.audio is not None
    assert inp.text is None


def test_batch_text_with_audio_raises() -> None:
    aud = AudioArtifact(data=b"\x00" * 10, mime_type=AudioMimeType.MP3)
    with pytest.raises(Exception, match="Batch text"):
        EmbeddingsInput(text=["a", "b"], audio=aud)
