"""Unit tests for Google embeddings multimodal request building (no network)."""

from pydantic import SecretStr

from celeste import Model
from celeste.artifacts import ImageArtifact, VideoArtifact
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import ImageMimeType, VideoMimeType
from celeste.modalities.embeddings.io import EmbeddingsInput
from celeste.modalities.embeddings.providers.google.client import GoogleEmbeddingsClient

_MODEL = Model(
    id="gemini-embedding-2-preview",
    provider=Provider.GOOGLE,
    display_name="Gemini Embedding 2 Preview",
    operations={Modality.EMBEDDINGS: {Operation.EMBED}},
)

_AUTH = AuthHeader(secret=SecretStr("test"), header="x-goog-api-key", prefix="")

_TEST_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
    b"\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00"
    b"\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _make_client() -> GoogleEmbeddingsClient:
    return GoogleEmbeddingsClient(
        model=_MODEL,
        provider=Provider.GOOGLE,
        auth=_AUTH,
    )


def test_text_only_single() -> None:
    client = _make_client()
    request = client._init_request(EmbeddingsInput(text="hello"))

    assert "content" in request
    assert request["content"]["parts"] == [{"text": "hello"}]
    assert "requests" not in request


def test_text_only_batch() -> None:
    client = _make_client()
    request = client._init_request(EmbeddingsInput(text=["a", "b"]))

    assert "requests" in request
    assert len(request["requests"]) == 2
    assert request["requests"][0]["content"]["parts"] == [{"text": "a"}]
    assert request["requests"][1]["content"]["parts"] == [{"text": "b"}]
    assert request["requests"][0]["model"] == "models/gemini-embedding-2-preview"


def test_single_image() -> None:
    client = _make_client()
    img = ImageArtifact(data=_TEST_PNG_BYTES, mime_type=ImageMimeType.PNG)
    request = client._init_request(EmbeddingsInput(images=img))

    assert "content" in request
    parts = request["content"]["parts"]
    assert len(parts) == 1
    assert "inline_data" in parts[0]
    assert parts[0]["inline_data"]["mime_type"] == "image/png"


def test_batch_images() -> None:
    client = _make_client()
    img1 = ImageArtifact(data=_TEST_PNG_BYTES, mime_type=ImageMimeType.PNG)
    img2 = ImageArtifact(data=_TEST_PNG_BYTES, mime_type=ImageMimeType.PNG)
    request = client._init_request(EmbeddingsInput(images=[img1, img2]))

    assert "requests" in request
    assert len(request["requests"]) == 2
    assert "inline_data" in request["requests"][0]["content"]["parts"][0]
    assert "inline_data" in request["requests"][1]["content"]["parts"][0]


def test_single_video() -> None:
    client = _make_client()
    vid = VideoArtifact(data=b"\x00" * 10, mime_type=VideoMimeType.MP4)
    request = client._init_request(EmbeddingsInput(videos=vid))

    assert "content" in request
    parts = request["content"]["parts"]
    assert len(parts) == 1
    assert "inline_data" in parts[0]
    assert parts[0]["inline_data"]["mime_type"] == "video/mp4"


def test_text_and_image_combined() -> None:
    client = _make_client()
    img = ImageArtifact(data=_TEST_PNG_BYTES, mime_type=ImageMimeType.PNG)
    request = client._init_request(EmbeddingsInput(text="a cat", images=img))

    assert "content" in request
    parts = request["content"]["parts"]
    assert len(parts) == 2
    assert parts[0] == {"text": "a cat"}
    assert "inline_data" in parts[1]


def test_image_with_url_uses_file_data() -> None:
    client = _make_client()
    img = ImageArtifact(url="https://example.com/image.png")
    request = client._init_request(EmbeddingsInput(images=img))

    parts = request["content"]["parts"]
    assert "file_data" in parts[0]
    assert parts[0]["file_data"]["file_uri"] == "https://example.com/image.png"
