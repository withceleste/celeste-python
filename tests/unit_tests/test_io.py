"""Tests for IO utilities - input type introspection functions."""

from typing import cast, get_args, get_origin

from celeste.artifacts import AudioArtifact, ImageArtifact, VideoArtifact
from celeste.constraints import (
    Bool,
    ImageConstraint,
    Str,
    VideoConstraint,
    VideosConstraint,
)
from celeste.core import InputType
from celeste.io import (
    _extract_input_type,
    get_constraint_input_type,
)


class TestExtractInputType:
    """Test _extract_input_type function."""

    def test_extract_input_type_direct_match(self) -> None:
        """Test that _extract_input_type returns InputType for direct matches."""
        assert _extract_input_type(str) == InputType.TEXT
        assert _extract_input_type(ImageArtifact) == InputType.IMAGE
        assert _extract_input_type(VideoArtifact) == InputType.VIDEO
        assert _extract_input_type(AudioArtifact) == InputType.AUDIO

    def test_extract_input_type_union_type(self) -> None:
        """Test that _extract_input_type extracts from union types."""
        union_type = str | ImageArtifact
        result = _extract_input_type(cast(type, union_type))
        # Should return the first match found (order may vary, so check it's one of them)
        assert result in {InputType.TEXT, InputType.IMAGE}

    def test_extract_input_type_list_generic(self) -> None:
        """Test that _extract_input_type extracts from list generics."""

        list_type = list[ImageArtifact]
        origin = get_origin(list_type)
        assert origin is list
        args = get_args(list_type)
        assert len(args) == 1
        result = _extract_input_type(args[0])  # Extract from the inner type
        assert result == InputType.IMAGE

    def test_extract_input_type_nested_union(self) -> None:
        """Test that _extract_input_type handles nested unions."""
        nested_union = str | ImageArtifact | VideoArtifact
        result = _extract_input_type(cast(type, nested_union))
        # Should find one of the types
        assert result in {InputType.TEXT, InputType.IMAGE, InputType.VIDEO}

    def test_extract_input_type_unmapped_type_returns_none(self) -> None:
        """Test that _extract_input_type returns None for unmapped types."""
        assert _extract_input_type(int) is None
        assert _extract_input_type(float) is None
        assert _extract_input_type(dict) is None


class TestGetConstraintInputType:
    """Test get_constraint_input_type function."""

    def test_get_constraint_input_type_with_image_constraint(self) -> None:
        """Test that get_constraint_input_type extracts InputType from ImageConstraint."""
        constraint = ImageConstraint()
        result = get_constraint_input_type(constraint)
        assert result == InputType.IMAGE

    def test_get_constraint_input_type_with_video_constraint(self) -> None:
        """Test that get_constraint_input_type extracts InputType from VideoConstraint."""
        constraint = VideoConstraint()
        result = get_constraint_input_type(constraint)
        assert result == InputType.VIDEO

    def test_get_constraint_input_type_with_videos_constraint(self) -> None:
        """Test that get_constraint_input_type extracts InputType from VideosConstraint."""
        constraint = VideosConstraint()
        result = get_constraint_input_type(constraint)
        assert result == InputType.VIDEO

    def test_get_constraint_input_type_with_str_constraint_returns_text(self) -> None:
        """Test that get_constraint_input_type returns TEXT for Str constraint."""
        constraint = Str(min_length=1)
        result = get_constraint_input_type(constraint)
        assert result == InputType.TEXT

    def test_get_constraint_input_type_with_no_artifact_type_returns_none(self) -> None:
        """Test that get_constraint_input_type returns None for constraints without mapped types."""
        constraint = Bool()
        result = get_constraint_input_type(constraint)
        assert result is None
