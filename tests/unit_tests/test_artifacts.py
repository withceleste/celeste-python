"""High-value tests for artifact classes - focusing on real-world usage patterns."""

from typing import Any

import pytest
from pydantic import ValidationError

from celeste.artifacts import Artifact, AudioArtifact, ImageArtifact, VideoArtifact
from celeste.mime_types import AudioMimeType, ImageMimeType, VideoMimeType


class TestArtifact:
    """Test base Artifact class behavior."""

    @pytest.mark.smoke
    @pytest.mark.parametrize(
        "storage_combo,expected",
        [
            # Single storage types
            ({"url": "https://example.com/file"}, True),
            ({"data": b"data"}, True),
            ({"path": "/path/to/file"}, True),
            # Empty artifact
            ({}, False),
            # Multiple storage types
            ({"url": "https://example.com", "data": b"data"}, True),
            ({"url": "https://example.com", "data": b"data", "path": "/path"}, True),
            # Edge case: all None explicitly
            ({"url": None, "data": None, "path": None}, False),
            # Edge case: empty string path (common mistake)
            ({"path": ""}, False),
        ],
        ids=[
            "single_url",
            "single_data",
            "single_path",
            "empty_artifact",
            "url_and_data",
            "all_storage_types",
            "all_none",
            "empty_string_path",
        ],
    )
    def test_has_content_with_storage_combinations(
        self, storage_combo: dict[str, Any], expected: bool
    ) -> None:
        """Test has_content correctly identifies content across all storage combinations."""
        artifact = Artifact(**storage_combo)
        assert artifact.has_content == expected

    def test_artifact_with_multiple_storage_types_preserves_values(self) -> None:
        """Artifact can have multiple storage types simultaneously (common in caching scenarios)."""
        artifact = Artifact(
            url="https://example.com/file.png",
            data=b"cached data",
            path="/cache/file.png",
        )
        assert artifact.has_content is True
        assert artifact.url == "https://example.com/file.png"
        assert artifact.data == b"cached data"
        assert artifact.path == "/cache/file.png"

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"url": "   "},
            {"path": "   "},
            {"url": "   ", "path": "   "},
        ],
        ids=["whitespace_url", "whitespace_path", "whitespace_both"],
    )
    def test_has_content_with_whitespace_only_strings(
        self, kwargs: dict[str, Any]
    ) -> None:
        """Whitespace-only strings should be treated as empty content."""
        assert Artifact(**kwargs).has_content is False

    def test_has_content_with_empty_string_url(self) -> None:
        """Empty string URLs should be treated as no content."""
        assert Artifact(url="").has_content is False

    def test_has_content_with_empty_bytes(self) -> None:
        """Empty bytes should be treated as no content."""
        assert Artifact(data=b"").has_content is False

    def test_artifact_metadata_default_behavior(self) -> None:
        """Artifact metadata defaults to empty dict."""
        artifact = Artifact(url="https://example.com/file.png")
        assert artifact.metadata == {}
        assert isinstance(artifact.metadata, dict)

    def test_artifact_metadata_setting_values(self) -> None:
        """Artifact metadata can store custom key-value pairs."""
        artifact = Artifact(
            url="https://example.com/file.png",
            metadata={"width": 1920, "height": 1080, "format": "png"},
        )
        assert artifact.metadata["width"] == 1920
        assert artifact.metadata["height"] == 1080
        assert artifact.metadata["format"] == "png"

    def test_artifact_metadata_is_mutable(self) -> None:
        """Artifact metadata dict can be modified after creation."""
        artifact = Artifact(url="https://example.com/file.png")
        artifact.metadata["custom"] = "value"
        assert artifact.metadata["custom"] == "value"

    def test_artifact_with_none_mime_type(self) -> None:
        """Artifact can have None mime_type."""
        artifact = Artifact(url="https://example.com/file.png", mime_type=None)
        assert artifact.mime_type is None
        assert artifact.has_content is True


class TestImageArtifact:
    """Test ImageArtifact specific behavior."""

    def test_image_artifact_accepts_image_mime_type(self) -> None:
        """ImageArtifact accepts valid image MIME types."""
        artifact = ImageArtifact(
            url="https://example.com/image.png", mime_type=ImageMimeType.PNG
        )
        assert artifact.mime_type == ImageMimeType.PNG

    def test_image_artifact_preserves_webp_mime_type(self) -> None:
        """ImageArtifact preserves WEBP MIME type."""
        artifact = ImageArtifact(data=b"webp data", mime_type=ImageMimeType.WEBP)
        assert artifact.mime_type == ImageMimeType.WEBP

    def test_image_artifact_accepts_none_mime_type(self) -> None:
        """ImageArtifact can have None mime_type."""
        artifact = ImageArtifact(url="https://example.com/image.png", mime_type=None)
        assert artifact.mime_type is None

    @pytest.mark.parametrize(
        "invalid_mime_type",
        [VideoMimeType.MP4, AudioMimeType.MP3],
        ids=["video_mime_type", "audio_mime_type"],
    )
    def test_image_artifact_rejects_invalid_mime_type(
        self, invalid_mime_type: VideoMimeType | AudioMimeType
    ) -> None:
        """ImageArtifact rejects non-image MIME types."""
        with pytest.raises(ValidationError, match=r".*mime_type.*"):
            ImageArtifact(
                url="https://example.com/file.png",
                mime_type=invalid_mime_type,  # type: ignore[arg-type]
            )


class TestVideoArtifact:
    """Test VideoArtifact specific behavior."""

    def test_video_artifact_accepts_video_mime_type(self) -> None:
        """VideoArtifact accepts valid video MIME types."""
        artifact = VideoArtifact(path="/videos/sample.mp4", mime_type=VideoMimeType.MP4)
        assert artifact.mime_type == VideoMimeType.MP4

    def test_video_artifact_accepts_none_mime_type(self) -> None:
        """VideoArtifact can have None mime_type."""
        artifact = VideoArtifact(path="/videos/sample.mp4", mime_type=None)
        assert artifact.mime_type is None

    @pytest.mark.parametrize(
        "invalid_mime_type",
        [ImageMimeType.PNG, AudioMimeType.MP3],
        ids=["image_mime_type", "audio_mime_type"],
    )
    def test_video_artifact_rejects_invalid_mime_type(
        self, invalid_mime_type: ImageMimeType | AudioMimeType
    ) -> None:
        """VideoArtifact rejects non-video MIME types."""
        with pytest.raises(ValidationError, match=r".*mime_type.*"):
            VideoArtifact(path="/videos/sample.mp4", mime_type=invalid_mime_type)  # type: ignore[arg-type]


class TestAudioArtifact:
    """Test AudioArtifact specific behavior."""

    @pytest.mark.parametrize("mime_type", [AudioMimeType.MP3, AudioMimeType.WAV])
    def test_audio_artifact_supports_common_formats(
        self, mime_type: AudioMimeType
    ) -> None:
        """AudioArtifact supports common audio formats."""
        artifact = AudioArtifact(
            url="https://example.com/audio",
            mime_type=mime_type,
        )
        assert artifact.mime_type == mime_type

    def test_audio_artifact_accepts_none_mime_type(self) -> None:
        """AudioArtifact can have None mime_type."""
        artifact = AudioArtifact(url="https://example.com/audio.mp3", mime_type=None)
        assert artifact.mime_type is None

    @pytest.mark.parametrize(
        "invalid_mime_type",
        [ImageMimeType.PNG, VideoMimeType.MP4],
        ids=["image_mime_type", "video_mime_type"],
    )
    def test_audio_artifact_rejects_invalid_mime_type(
        self, invalid_mime_type: ImageMimeType | VideoMimeType
    ) -> None:
        """AudioArtifact rejects non-audio MIME types."""
        with pytest.raises(ValidationError, match=r".*mime_type.*"):
            AudioArtifact(
                url="https://example.com/audio.mp3",
                mime_type=invalid_mime_type,  # type: ignore[arg-type]
            )
