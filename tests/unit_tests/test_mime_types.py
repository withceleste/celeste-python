"""High-value tests for MIME type enums - focusing on inheritance and string behavior."""

import json
from enum import Enum

import pytest

from celeste.mime_types import AudioMimeType, ImageMimeType, MimeType, VideoMimeType


class TestMimeTypeInheritance:
    """Test the MIME type enum inheritance structure."""

    def test_all_mime_types_inherit_from_base(self) -> None:
        """All specific MIME type enums should inherit from MimeType base class."""
        assert issubclass(ImageMimeType, MimeType)
        assert issubclass(VideoMimeType, MimeType)
        assert issubclass(AudioMimeType, MimeType)

    def test_mime_type_base_is_string_enum(self) -> None:
        """MimeType should be both a string and Enum (StrEnum pattern)."""
        assert issubclass(MimeType, str)
        assert issubclass(MimeType, Enum)

    @pytest.mark.parametrize(
        "mime_type,expected_value",
        [
            (ImageMimeType.PNG, "image/png"),
            (ImageMimeType.JPEG, "image/jpeg"),
            (VideoMimeType.MP4, "video/mp4"),
            (AudioMimeType.MP3, "audio/mpeg"),
            (AudioMimeType.WAV, "audio/wav"),
        ],
    )
    def test_mime_types_equal_their_string_values(
        self, mime_type: MimeType, expected_value: str
    ) -> None:
        """MIME types should equal their string values for API compatibility."""
        assert mime_type == expected_value
        assert mime_type.value == expected_value


class TestImageMimeType:
    """Test ImageMimeType specific values and behavior."""

    def test_image_mime_type_values(self) -> None:
        """ImageMimeType should have correct MIME type strings."""
        assert ImageMimeType.PNG.value == "image/png"
        assert ImageMimeType.JPEG.value == "image/jpeg"

    def test_image_mime_type_members_exist(self) -> None:
        """ImageMimeType should contain expected members."""
        members = list(ImageMimeType)
        assert ImageMimeType.PNG in members
        assert ImageMimeType.JPEG in members


class TestVideoMimeType:
    """Test VideoMimeType specific values and behavior."""

    def test_video_mime_type_values(self) -> None:
        """VideoMimeType should have correct MIME type strings."""
        assert VideoMimeType.MP4.value == "video/mp4"

    def test_video_mime_type_members_exist(self) -> None:
        """VideoMimeType should contain expected members."""
        members = list(VideoMimeType)
        assert VideoMimeType.MP4 in members


class TestAudioMimeType:
    """Test AudioMimeType specific values and behavior."""

    def test_audio_mime_type_values(self) -> None:
        """AudioMimeType should have correct MIME type strings."""
        assert AudioMimeType.MP3.value == "audio/mpeg"
        assert AudioMimeType.WAV.value == "audio/wav"


class TestMimeTypeUsagePatterns:
    """Test common usage patterns and edge cases."""

    def test_mime_type_json_serialization(self) -> None:
        """MIME types should serialize to JSON correctly."""
        # Critical for API responses
        mime_dict = {
            "image": ImageMimeType.JPEG,
            "video": VideoMimeType.MP4,
            "audio": AudioMimeType.MP3,
        }

        # Should serialize without custom encoder
        json_str = json.dumps(mime_dict)
        loaded = json.loads(json_str)

        assert loaded["image"] == "image/jpeg"
        assert loaded["video"] == "video/mp4"
        assert loaded["audio"] == "audio/mpeg"

    def test_mime_type_membership_check(self) -> None:
        """Test 'in' operator works with MIME type enums."""
        # Common pattern for validation
        valid_image_types = [ImageMimeType.PNG, ImageMimeType.JPEG]
        assert ImageMimeType.PNG in valid_image_types
        assert VideoMimeType.MP4 not in valid_image_types  # type: ignore[comparison-overlap]

    @pytest.mark.parametrize(
        "mime_type,expected_category",
        [
            (ImageMimeType.PNG, "image"),
            (ImageMimeType.JPEG, "image"),
            (VideoMimeType.MP4, "video"),
            (AudioMimeType.MP3, "audio"),
            (AudioMimeType.WAV, "audio"),
        ],
    )
    def test_mime_type_category_extraction(
        self, mime_type: MimeType, expected_category: str
    ) -> None:
        """Test extracting category from MIME type string (common parsing need)."""
        # Tests the string nature of our enums
        category = mime_type.value.split("/")[0]
        assert category == expected_category


class TestMimeTypeErrorCases:
    """Test error handling and edge cases."""

    def test_invalid_mime_type_comparison(self) -> None:
        """Different MIME type categories should not be equal."""
        assert ImageMimeType.PNG != VideoMimeType.MP4  # type: ignore[comparison-overlap]
        assert ImageMimeType.PNG != AudioMimeType.MP3  # type: ignore[comparison-overlap]
        assert VideoMimeType.MP4 != AudioMimeType.WAV  # type: ignore[comparison-overlap]

    def test_mime_type_case_sensitivity(self) -> None:
        """MIME types should be case-sensitive (per RFC standard)."""
        assert ImageMimeType.PNG != "IMAGE/PNG"  # type: ignore[comparison-overlap]
        assert ImageMimeType.PNG == "image/png"  # type: ignore[comparison-overlap]

    def test_cannot_create_invalid_mime_type(self) -> None:
        """Cannot instantiate invalid MIME type enum values."""
        with pytest.raises(ValueError):
            ImageMimeType("invalid/type")

    def test_mime_type_hashable(self) -> None:
        """MIME types should be hashable for use in sets/dicts."""
        # Important for caching and deduplication
        mime_set = {ImageMimeType.PNG, ImageMimeType.JPEG, ImageMimeType.PNG}
        assert len(mime_set) == 2  # PNG should be deduplicated

        mime_dict = {
            ImageMimeType.PNG: "png_handler",
            ImageMimeType.JPEG: "jpeg_handler",
        }
        assert mime_dict[ImageMimeType.PNG] == "png_handler"
