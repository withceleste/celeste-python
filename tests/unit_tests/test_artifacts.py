import base64
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from celeste.artifacts import (
    Artifact,
    AudioArtifact,
    DocumentArtifact,
    ImageArtifact,
    VideoArtifact,
)
from celeste.mime_types import (
    AudioMimeType,
    DocumentMimeType,
    ImageMimeType,
    VideoMimeType,
)
from celeste.utils import build_data_url


@pytest.mark.parametrize(
    ("fields", "expected"),
    [
        ({"url": "https://example.com/file"}, True),
        ({"data": b"data"}, True),
        ({"path": "file.bin"}, True),
        ({"url": " ", "path": "\t", "data": b""}, False),
        ({}, False),
    ],
)
def test_has_content(fields: dict[str, Any], expected: bool) -> None:
    assert Artifact(**fields).has_content is expected


@pytest.mark.parametrize(
    ("artifact_type", "valid_mime", "invalid_mime"),
    [
        (ImageArtifact, ImageMimeType.PNG, VideoMimeType.MP4),
        (VideoArtifact, VideoMimeType.MP4, AudioMimeType.MP3),
        (AudioArtifact, AudioMimeType.MP3, ImageMimeType.PNG),
        (DocumentArtifact, DocumentMimeType.PDF, ImageMimeType.PNG),
    ],
)
def test_specialized_artifact_mime_boundary(
    artifact_type: type[Artifact], valid_mime: object, invalid_mime: object
) -> None:
    assert artifact_type(data=b"content", mime_type=valid_mime).mime_type == valid_mime
    with pytest.raises(ValidationError, match="mime_type"):
        artifact_type(data=b"content", mime_type=invalid_mime)


def test_get_bytes_prefers_data_then_reads_path(tmp_path: Path) -> None:
    path = tmp_path / "artifact.bin"
    path.write_bytes(b"disk")

    assert Artifact(data=b"memory", path=str(path)).get_bytes() == b"memory"
    assert Artifact(path=str(path)).get_bytes() == b"disk"


@pytest.mark.parametrize("artifact", [Artifact(), Artifact(url="https://example.com")])
def test_get_bytes_requires_local_content(artifact: Artifact) -> None:
    with pytest.raises(ValueError, match="data or path"):
        artifact.get_bytes()


def test_build_data_url_requires_mime_type() -> None:
    with pytest.raises(ValueError, match="MIME type"):
        build_data_url(Artifact(data=b"unknown"))


def test_data_json_and_base64_round_trip() -> None:
    raw = b"binary content"
    encoded = Artifact(data=raw).model_dump(mode="json")["data"]

    assert encoded == base64.b64encode(raw).decode("ascii")
    assert (
        Artifact.model_validate_json(Artifact(data=raw).model_dump_json()).data == raw
    )
    assert Artifact(data=raw).get_base64() == encoded
