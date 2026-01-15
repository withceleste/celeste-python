"""Tests for constraint validation models."""

import pytest
from pydantic import BaseModel

from celeste.artifacts import AudioArtifact, ImageArtifact, VideoArtifact
from celeste.constraints import (
    AudioConstraint,
    AudiosConstraint,
    Bool,
    Choice,
    Float,
    ImageConstraint,
    ImagesConstraint,
    Int,
    Pattern,
    Range,
    Schema,
    Str,
    VideoConstraint,
    VideosConstraint,
)
from celeste.exceptions import ConstraintViolationError
from celeste.mime_types import AudioMimeType, ImageMimeType, VideoMimeType


class TestChoice:
    """Test Choice constraint validation."""

    @pytest.mark.smoke
    def test_validates_value_in_options(self) -> None:
        """Test that valid choice passes validation."""
        constraint = Choice[str](options=["a", "b", "c"])

        result = constraint("b")

        assert result == "b"

    def test_rejects_value_not_in_options(self) -> None:
        """Test that invalid choice raises ConstraintViolationError."""
        constraint = Choice[str](options=["a", "b", "c"])

        with pytest.raises(
            ConstraintViolationError, match=r"Must be one of \['a', 'b', 'c'\], got 'd'"
        ):
            constraint("d")

    def test_works_with_numeric_types(self) -> None:
        """Test Choice works with int/float options."""
        constraint = Choice[int](options=[1, 2, 3])

        result = constraint(2)

        assert result == 2

    def test_rejects_empty_options_list(self) -> None:
        """Test Choice construction fails with empty options."""
        with pytest.raises(ValueError):
            Choice[str](options=[])


class TestRange:
    """Test Range constraint validation."""

    @pytest.mark.smoke
    def test_validates_value_within_range(self) -> None:
        """Test that value within bounds passes validation."""
        constraint = Range(min=0.0, max=1.0)

        result = constraint(0.5)

        assert result == 0.5

    def test_validates_boundary_values(self) -> None:
        """Test that min/max boundary values are inclusive."""
        constraint = Range(min=0, max=10)

        assert constraint(0) == 0
        assert constraint(10) == 10

    def test_rejects_value_below_min(self) -> None:
        """Test that value below min raises ConstraintViolationError."""
        constraint = Range(min=0, max=10)

        with pytest.raises(
            ConstraintViolationError, match=r"Must be between 0 and 10, got -1"
        ):
            constraint(-1)

    def test_rejects_value_above_max(self) -> None:
        """Test that value above max raises ConstraintViolationError."""
        constraint = Range(min=0, max=10)

        with pytest.raises(
            ConstraintViolationError, match=r"Must be between 0 and 10, got 11"
        ):
            constraint(11)

    def test_rejects_non_numeric_value(self) -> None:
        """Test that non-numeric value raises ConstraintViolationError."""
        constraint = Range(min=0, max=10)

        with pytest.raises(ConstraintViolationError, match=r"Must be numeric, got str"):
            constraint("5")  # type: ignore[arg-type]

    def test_accepts_both_int_and_float(self) -> None:
        """Test Range accepts both int and float values."""
        constraint = Range(min=0.0, max=10.0)

        assert constraint(5) == 5  # int
        assert constraint(5.5) == 5.5  # float

    def test_validates_value_with_step(self) -> None:
        """Test that value at valid step increment passes."""
        constraint = Range(min=0, max=10, step=2)

        assert constraint(0) == 0  # min
        assert constraint(2) == 2
        assert constraint(4) == 4
        assert constraint(10) == 10  # max

    def test_rejects_value_not_on_step(self) -> None:
        """Test that value not on step increment raises ConstraintViolationError."""
        constraint = Range(min=0, max=10, step=2)

        with pytest.raises(
            ConstraintViolationError,
            match=r"Value must match step 2(\.0)?. Nearest valid: 2(\.0)? or 4(\.0)?, got 3",
        ):
            constraint(3)

    def test_validates_float_step(self) -> None:
        """Test step validation with float increments."""
        constraint = Range(min=0.0, max=1.0, step=0.25)

        assert constraint(0.0) == 0.0
        assert constraint(0.25) == 0.25
        assert constraint(0.5) == 0.5
        assert constraint(0.75) == 0.75
        assert constraint(1.0) == 1.0

    def test_step_validation_with_non_zero_min(self) -> None:
        """Test step validation calculates offset from min correctly."""
        constraint = Range(min=5, max=15, step=3)

        assert constraint(5) == 5  # min
        assert constraint(8) == 8  # min + 3
        assert constraint(11) == 11  # min + 6
        assert constraint(14) == 14  # min + 9

        with pytest.raises(
            ConstraintViolationError,
            match=r"Value must match step 3(\.0)?. Nearest valid: 5(\.0)? or 8(\.0)?, got 7",
        ):
            constraint(7)

    def test_step_validation_handles_float_precision(self) -> None:
        """Test step validation handles floating-point precision issues."""
        constraint = Range(min=0.0, max=2.0, step=0.1)

        # These should all pass despite potential float precision issues
        assert constraint(0.0) == 0.0
        assert constraint(0.1) == 0.1
        assert constraint(0.7) == 0.7
        assert constraint(1.0) == 1.0
        assert constraint(2.0) == 2.0

    def test_validates_value_near_step_within_epsilon(self) -> None:
        """Range validates values within epsilon tolerance of valid step."""
        constraint = Range(min=0.0, max=10.0, step=0.1)

        # Test values that might have floating-point precision issues
        # 0.1 + 0.1 + 0.1 might be 0.30000000000000004 due to float representation
        result = constraint(0.1 + 0.1 + 0.1)  # Should be ~0.3
        assert result == pytest.approx(0.3)

        # Test another precision edge case
        result2 = constraint(0.7)  # Should pass within epsilon
        assert result2 == pytest.approx(0.7)


class TestPattern:
    """Test Pattern constraint validation."""

    @pytest.mark.smoke
    def test_validates_matching_pattern(self) -> None:
        """Test that string matching pattern passes validation."""
        constraint = Pattern(pattern=r"^\d{3}-\d{4}$")

        result = constraint("123-4567")

        assert result == "123-4567"

    def test_rejects_non_matching_pattern(self) -> None:
        """Test that non-matching pattern raises ConstraintViolationError."""
        constraint = Pattern(pattern=r"^\d{3}-\d{4}$")

        with pytest.raises(ConstraintViolationError, match=r"Must match pattern"):
            constraint("abc-defg")

    def test_rejects_non_string_value(self) -> None:
        """Test that non-string value raises ConstraintViolationError."""
        constraint = Pattern(pattern=r"^\d+$")

        with pytest.raises(ConstraintViolationError, match=r"Must be string, got int"):
            constraint(123)  # type: ignore[arg-type]

    def test_validates_complex_regex_patterns(self) -> None:
        """Test Pattern works with complex regex."""
        # Email-like pattern
        constraint = Pattern(pattern=r"^[a-z]+@[a-z]+\.[a-z]+$")

        result = constraint("user@domain.com")

        assert result == "user@domain.com"


class TestStr:
    """Test Str constraint validation."""

    @pytest.mark.smoke
    def test_validates_string_without_length_constraints(self) -> None:
        """Test that any string passes when no length constraints set."""
        constraint = Str()

        result = constraint("any string")

        assert result == "any string"

    def test_validates_string_within_length_bounds(self) -> None:
        """Test string within min/max length passes."""
        constraint = Str(min_length=2, max_length=10)

        result = constraint("valid")

        assert result == "valid"

    def test_rejects_string_below_min_length(self) -> None:
        """Test string shorter than min_length raises ConstraintViolationError."""
        constraint = Str(min_length=5)

        with pytest.raises(
            ConstraintViolationError, match=r"String too short \(min 5\), got length 3"
        ):
            constraint("abc")

    def test_rejects_string_above_max_length(self) -> None:
        """Test string longer than max_length raises ConstraintViolationError."""
        constraint = Str(max_length=5)

        with pytest.raises(
            ConstraintViolationError, match=r"String too long \(max 5\), got length 10"
        ):
            constraint("too long!!")

    def test_rejects_non_string_value(self) -> None:
        """Test non-string value raises ConstraintViolationError."""
        constraint = Str()

        with pytest.raises(ConstraintViolationError, match=r"Must be string, got int"):
            constraint(123)  # type: ignore[arg-type]

    def test_validates_boundary_lengths(self) -> None:
        """Test exact min/max length strings are valid."""
        constraint = Str(min_length=3, max_length=5)

        assert constraint("abc") == "abc"  # min
        assert constraint("abcde") == "abcde"  # max


class TestInt:
    """Test Int constraint validation."""

    @pytest.mark.smoke
    def test_validates_integer_value(self) -> None:
        """Test that integer passes validation."""
        constraint = Int()

        result = constraint(42)

        assert result == 42

    def test_converts_whole_float_to_int(self) -> None:
        """Test that whole float is converted to int."""
        constraint = Int()

        result = constraint(42.0)

        assert result == 42
        assert isinstance(result, int)

    def test_rejects_non_whole_float(self) -> None:
        """Test that non-whole float raises ConstraintViolationError."""
        constraint = Int()

        with pytest.raises(ConstraintViolationError, match=r"Must be int, got 42\.5"):
            constraint(42.5)

    def test_accepts_boolean_value(self) -> None:
        """Test that bool is accepted (bool is subclass of int in Python)."""
        constraint = Int()

        assert constraint(True) == 1
        assert constraint(False) == 0

    def test_converts_valid_string_to_int(self) -> None:
        """Test that valid integer string is converted to int."""
        constraint = Int()

        result = constraint("42")

        assert result == 42
        assert isinstance(result, int)

    def test_rejects_invalid_string(self) -> None:
        """Test that non-integer string raises ConstraintViolationError."""
        constraint = Int()

        with pytest.raises(ConstraintViolationError, match=r"Must be int, got 'abc'"):
            constraint("abc")


class TestFloat:
    """Test Float constraint validation."""

    @pytest.mark.smoke
    def test_validates_float_value(self) -> None:
        """Test that float passes validation."""
        constraint = Float()

        result = constraint(3.14)

        assert result == 3.14

    def test_accepts_and_converts_int_to_float(self) -> None:
        """Test that int is accepted and converted to float."""
        constraint = Float()

        result = constraint(42)

        assert result == 42.0
        assert isinstance(result, float)

    def test_rejects_boolean_value(self) -> None:
        """Test that bool raises ConstraintViolationError despite isinstance(True, int)."""
        constraint = Float()

        with pytest.raises(
            ConstraintViolationError, match=r"Must be float or int, got bool"
        ):
            constraint(True)

    def test_rejects_string_value(self) -> None:
        """Test that string raises ConstraintViolationError."""
        constraint = Float()

        with pytest.raises(
            ConstraintViolationError, match=r"Must be float or int, got str"
        ):
            constraint("3.14")  # type: ignore[arg-type]


class TestBool:
    """Test Bool constraint validation."""

    @pytest.mark.smoke
    def test_validates_boolean_value(self) -> None:
        """Test that bool passes validation."""
        constraint = Bool()

        assert constraint(True) is True
        assert constraint(False) is False

    def test_rejects_int_value(self) -> None:
        """Test that int raises ConstraintViolationError (no implicit 0/1 conversion)."""
        constraint = Bool()

        with pytest.raises(ConstraintViolationError, match=r"Must be bool, got int"):
            constraint(1)  # type: ignore[arg-type]

    def test_rejects_string_value(self) -> None:
        """Test that string raises ConstraintViolationError."""
        constraint = Bool()

        with pytest.raises(ConstraintViolationError, match=r"Must be bool, got str"):
            constraint("true")  # type: ignore[arg-type]


class TestRangeSpecialValues:
    """Test Range constraint special_values bypass behavior."""

    def test_special_values_bypass_bounds(self) -> None:
        """Values in special_values bypass min/max validation."""
        constraint = Range(min=0, max=10, special_values=[-1, 100])

        # These are outside bounds but allowed via special_values
        assert constraint(-1) == -1
        assert constraint(100) == 100

    def test_non_special_values_still_validated(self) -> None:
        """Values not in special_values get normal bounds validation."""
        constraint = Range(min=0, max=10, special_values=[-1])

        # -2 is not in special_values, so bounds apply
        with pytest.raises(ConstraintViolationError, match=r"Must be between 0 and 10"):
            constraint(-2)

    def test_normal_values_with_special_values_defined(self) -> None:
        """Normal values within bounds still work when special_values defined."""
        constraint = Range(min=0, max=10, special_values=[-1, 100])

        assert constraint(5) == 5
        assert constraint(0) == 0
        assert constraint(10) == 10


class TestSchema:
    """Test Schema constraint validation."""

    def test_validates_basemodel_subclass(self) -> None:
        """Schema accepts valid BaseModel subclass."""

        class MyModel(BaseModel):
            name: str

        constraint = Schema()
        result = constraint(MyModel)

        assert result is MyModel

    def test_rejects_non_basemodel_type(self) -> None:
        """Schema rejects types that aren't BaseModel subclasses."""
        constraint = Schema()

        with pytest.raises(ConstraintViolationError, match=r"Must be BaseModel"):
            constraint(str)  # type: ignore[arg-type]

    def test_validates_list_basemodel_type_hint(self) -> None:
        """Schema accepts list[BaseModel] type hints."""

        class MyModel(BaseModel):
            value: int

        constraint = Schema()
        result = constraint(list[MyModel])  # type: ignore[arg-type]

        assert result == list[MyModel]  # type: ignore[comparison-overlap]

    def test_rejects_list_of_non_models(self) -> None:
        """Schema rejects list[T] where T is not a BaseModel subclass."""
        constraint = Schema()

        with pytest.raises(
            ConstraintViolationError, match=r"List type must be BaseModel"
        ):
            constraint(list[str])  # type: ignore[arg-type]


class TestImageConstraint:
    """Test ImageConstraint validation for single image artifacts."""

    def test_rejects_list_input(self) -> None:
        """ImageConstraint requires single artifact, not a list."""
        constraint = ImageConstraint()
        artifact = ImageArtifact(data=b"test")

        with pytest.raises(
            ConstraintViolationError,
            match=r"requires a single ImageArtifact, not a list",
        ):
            constraint([artifact])  # type: ignore[arg-type]

    def test_validates_image_artifact_type(self) -> None:
        """ImageConstraint rejects non-ImageArtifact types."""
        constraint = ImageConstraint()

        with pytest.raises(ConstraintViolationError, match=r"Must be ImageArtifact"):
            constraint("not an artifact")  # type: ignore[arg-type]

    def test_accepts_valid_artifact(self) -> None:
        """Valid ImageArtifact passes through unchanged."""
        constraint = ImageConstraint()
        artifact = ImageArtifact(data=b"test image data")

        result = constraint(artifact)

        assert result is artifact

    def test_filters_mime_types_when_specified(self) -> None:
        """ImageConstraint rejects unsupported MIME types."""
        constraint = ImageConstraint(supported_mime_types=[ImageMimeType.PNG])
        jpeg_artifact = ImageArtifact(data=b"test", mime_type=ImageMimeType.JPEG)

        with pytest.raises(ConstraintViolationError, match=r"mime_type must be one of"):
            constraint(jpeg_artifact)

    def test_accepts_supported_mime_type(self) -> None:
        """ImageConstraint accepts artifact with supported MIME type."""
        constraint = ImageConstraint(supported_mime_types=[ImageMimeType.PNG])
        png_artifact = ImageArtifact(data=b"test", mime_type=ImageMimeType.PNG)

        result = constraint(png_artifact)

        assert result is png_artifact

    def test_accepts_any_mime_when_none_specified(self) -> None:
        """No MIME filtering when supported_mime_types is None."""
        constraint = ImageConstraint(supported_mime_types=None)
        artifact = ImageArtifact(data=b"test", mime_type=ImageMimeType.JPEG)

        result = constraint(artifact)

        assert result is artifact


class TestImagesConstraint:
    """Test ImagesConstraint validation for image artifact lists."""

    def test_normalizes_single_artifact_to_list(self) -> None:
        """Single ImageArtifact is wrapped in a list."""
        constraint = ImagesConstraint()
        artifact = ImageArtifact(data=b"test")

        result = constraint(artifact)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] is artifact

    def test_accepts_list_of_artifacts(self) -> None:
        """List of ImageArtifacts passes through."""
        constraint = ImagesConstraint()
        artifacts = [ImageArtifact(data=b"1"), ImageArtifact(data=b"2")]

        result = constraint(artifacts)

        assert result == artifacts

    def test_enforces_max_count(self) -> None:
        """ImagesConstraint rejects when count exceeds max_count."""
        constraint = ImagesConstraint(max_count=2)
        artifacts = [ImageArtifact(data=b"x") for _ in range(3)]

        with pytest.raises(ConstraintViolationError, match=r"at most 2 image"):
            constraint(artifacts)

    def test_validates_each_artifact_type(self) -> None:
        """ImagesConstraint reports index (1-indexed) of invalid artifact."""
        constraint = ImagesConstraint(supported_mime_types=[ImageMimeType.PNG])
        artifacts = [
            ImageArtifact(data=b"1", mime_type=ImageMimeType.PNG),
            "not an artifact",  # Invalid at index 2
            ImageArtifact(data=b"3", mime_type=ImageMimeType.PNG),
        ]

        with pytest.raises(
            ConstraintViolationError, match=r"Image 2.*Must be ImageArtifact"
        ):
            constraint(artifacts)  # type: ignore[arg-type]

    def test_filters_mime_types_per_image(self) -> None:
        """Each image's MIME type is validated against supported types."""
        constraint = ImagesConstraint(supported_mime_types=[ImageMimeType.PNG])
        artifacts = [
            ImageArtifact(data=b"1", mime_type=ImageMimeType.PNG),
            ImageArtifact(data=b"2", mime_type=ImageMimeType.JPEG),  # Invalid
        ]

        with pytest.raises(
            ConstraintViolationError, match=r"Image 2.*mime_type must be one of"
        ):
            constraint(artifacts)

    def test_handles_empty_list(self) -> None:
        """Empty list is valid (no images to validate)."""
        constraint = ImagesConstraint()

        result = constraint([])

        assert result == []

    def test_accepts_all_valid_images(self) -> None:
        """All images with valid MIME types pass validation."""
        constraint = ImagesConstraint(
            supported_mime_types=[ImageMimeType.PNG, ImageMimeType.JPEG]
        )
        artifacts = [
            ImageArtifact(data=b"1", mime_type=ImageMimeType.PNG),
            ImageArtifact(data=b"2", mime_type=ImageMimeType.JPEG),
        ]

        result = constraint(artifacts)

        assert result == artifacts


class TestVideoConstraint:
    """Test VideoConstraint validation for single video artifacts."""

    def test_rejects_list_input(self) -> None:
        """VideoConstraint requires single artifact, not a list."""
        constraint = VideoConstraint()
        artifact = VideoArtifact(data=b"test")

        with pytest.raises(
            ConstraintViolationError,
            match=r"requires a single VideoArtifact, not a list",
        ):
            constraint([artifact])  # type: ignore[arg-type]

    def test_validates_video_artifact_type(self) -> None:
        """VideoConstraint rejects non-VideoArtifact types."""
        constraint = VideoConstraint()

        with pytest.raises(ConstraintViolationError, match=r"Must be VideoArtifact"):
            constraint("not an artifact")  # type: ignore[arg-type]

    def test_accepts_valid_artifact(self) -> None:
        """Valid VideoArtifact passes through unchanged."""
        constraint = VideoConstraint()
        artifact = VideoArtifact(data=b"test video data")

        result = constraint(artifact)

        assert result is artifact

    def test_filters_mime_types_when_specified(self) -> None:
        """VideoConstraint rejects unsupported MIME types."""
        constraint = VideoConstraint(supported_mime_types=[VideoMimeType.MP4])
        webm_artifact = VideoArtifact(data=b"test", mime_type=VideoMimeType.MOV)

        with pytest.raises(ConstraintViolationError, match=r"mime_type must be one of"):
            constraint(webm_artifact)

    def test_accepts_supported_mime_type(self) -> None:
        """VideoConstraint accepts artifact with supported MIME type."""
        constraint = VideoConstraint(supported_mime_types=[VideoMimeType.MP4])
        mp4_artifact = VideoArtifact(data=b"test", mime_type=VideoMimeType.MP4)

        result = constraint(mp4_artifact)

        assert result is mp4_artifact

    def test_accepts_any_mime_when_none_specified(self) -> None:
        """No MIME filtering when supported_mime_types is None."""
        constraint = VideoConstraint(supported_mime_types=None)
        artifact = VideoArtifact(data=b"test", mime_type=VideoMimeType.MOV)

        result = constraint(artifact)

        assert result is artifact


class TestVideosConstraint:
    """Test VideosConstraint validation for video artifact lists."""

    def test_normalizes_single_artifact_to_list(self) -> None:
        """Single VideoArtifact is wrapped in a list."""
        constraint = VideosConstraint()
        artifact = VideoArtifact(data=b"test")

        result = constraint(artifact)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] is artifact

    def test_accepts_list_of_artifacts(self) -> None:
        """List of VideoArtifacts passes through."""
        constraint = VideosConstraint()
        artifacts = [VideoArtifact(data=b"1"), VideoArtifact(data=b"2")]

        result = constraint(artifacts)

        assert result == artifacts

    def test_enforces_max_count(self) -> None:
        """VideosConstraint rejects when count exceeds max_count."""
        constraint = VideosConstraint(max_count=2)
        artifacts = [VideoArtifact(data=b"x") for _ in range(3)]

        with pytest.raises(ConstraintViolationError, match=r"at most 2 video"):
            constraint(artifacts)

    def test_validates_each_artifact_type(self) -> None:
        """VideosConstraint reports index (1-indexed) of invalid artifact."""
        constraint = VideosConstraint(supported_mime_types=[VideoMimeType.MP4])
        artifacts = [
            VideoArtifact(data=b"1", mime_type=VideoMimeType.MP4),
            "not an artifact",  # Invalid at index 2
            VideoArtifact(data=b"3", mime_type=VideoMimeType.MP4),
        ]

        with pytest.raises(
            ConstraintViolationError, match=r"Video 2.*Must be VideoArtifact"
        ):
            constraint(artifacts)  # type: ignore[arg-type]

    def test_filters_mime_types_per_video(self) -> None:
        """Each video's MIME type is validated against supported types."""
        constraint = VideosConstraint(supported_mime_types=[VideoMimeType.MP4])
        artifacts = [
            VideoArtifact(data=b"1", mime_type=VideoMimeType.MP4),
            VideoArtifact(data=b"2", mime_type=VideoMimeType.MOV),  # Invalid
        ]

        with pytest.raises(
            ConstraintViolationError, match=r"Video 2.*mime_type must be one of"
        ):
            constraint(artifacts)

    def test_handles_empty_list(self) -> None:
        """Empty list is valid (no videos to validate)."""
        constraint = VideosConstraint()

        result = constraint([])

        assert result == []

    def test_accepts_all_valid_videos(self) -> None:
        """All videos with valid MIME types pass validation."""
        constraint = VideosConstraint(
            supported_mime_types=[VideoMimeType.MP4, VideoMimeType.MOV]
        )
        artifacts = [
            VideoArtifact(data=b"1", mime_type=VideoMimeType.MP4),
            VideoArtifact(data=b"2", mime_type=VideoMimeType.MOV),
        ]

        result = constraint(artifacts)

        assert result == artifacts


class TestAudioConstraint:
    """Test AudioConstraint validation for single audio artifacts."""

    def test_rejects_list_input(self) -> None:
        """AudioConstraint requires single artifact, not a list."""
        constraint = AudioConstraint()
        artifact = AudioArtifact(data=b"test")

        with pytest.raises(
            ConstraintViolationError,
            match=r"requires a single AudioArtifact, not a list",
        ):
            constraint([artifact])  # type: ignore[arg-type]

    def test_validates_audio_artifact_type(self) -> None:
        """AudioConstraint rejects non-AudioArtifact types."""
        constraint = AudioConstraint()

        with pytest.raises(ConstraintViolationError, match=r"Must be AudioArtifact"):
            constraint("not an artifact")  # type: ignore[arg-type]

    def test_accepts_valid_artifact(self) -> None:
        """Valid AudioArtifact passes through unchanged."""
        constraint = AudioConstraint()
        artifact = AudioArtifact(data=b"test audio data")

        result = constraint(artifact)

        assert result is artifact

    def test_filters_mime_types_when_specified(self) -> None:
        """AudioConstraint rejects unsupported MIME types."""
        constraint = AudioConstraint(supported_mime_types=[AudioMimeType.MP3])
        wav_artifact = AudioArtifact(data=b"test", mime_type=AudioMimeType.WAV)

        with pytest.raises(ConstraintViolationError, match=r"mime_type must be one of"):
            constraint(wav_artifact)

    def test_accepts_supported_mime_type(self) -> None:
        """AudioConstraint accepts artifact with supported MIME type."""
        constraint = AudioConstraint(supported_mime_types=[AudioMimeType.MP3])
        mp3_artifact = AudioArtifact(data=b"test", mime_type=AudioMimeType.MP3)

        result = constraint(mp3_artifact)

        assert result is mp3_artifact

    def test_accepts_any_mime_when_none_specified(self) -> None:
        """No MIME filtering when supported_mime_types is None."""
        constraint = AudioConstraint(supported_mime_types=None)
        artifact = AudioArtifact(data=b"test", mime_type=AudioMimeType.WAV)

        result = constraint(artifact)

        assert result is artifact


class TestAudiosConstraint:
    """Test AudiosConstraint validation for audio artifact lists."""

    def test_normalizes_single_artifact_to_list(self) -> None:
        """Single AudioArtifact is wrapped in a list."""
        constraint = AudiosConstraint()
        artifact = AudioArtifact(data=b"test")

        result = constraint(artifact)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] is artifact

    def test_accepts_list_of_artifacts(self) -> None:
        """List of AudioArtifacts passes through."""
        constraint = AudiosConstraint()
        artifacts = [AudioArtifact(data=b"1"), AudioArtifact(data=b"2")]

        result = constraint(artifacts)

        assert result == artifacts

    def test_enforces_max_count(self) -> None:
        """AudiosConstraint rejects when count exceeds max_count."""
        constraint = AudiosConstraint(max_count=2)
        artifacts = [AudioArtifact(data=b"x") for _ in range(3)]

        with pytest.raises(ConstraintViolationError, match=r"at most 2 audio"):
            constraint(artifacts)

    def test_validates_each_artifact_type(self) -> None:
        """AudiosConstraint reports index (1-indexed) of invalid artifact."""
        constraint = AudiosConstraint(supported_mime_types=[AudioMimeType.MP3])
        artifacts = [
            AudioArtifact(data=b"1", mime_type=AudioMimeType.MP3),
            "not an artifact",  # Invalid at index 2
            AudioArtifact(data=b"3", mime_type=AudioMimeType.MP3),
        ]

        with pytest.raises(
            ConstraintViolationError, match=r"Audio 2.*Must be AudioArtifact"
        ):
            constraint(artifacts)  # type: ignore[arg-type]

    def test_filters_mime_types_per_audio(self) -> None:
        """Each audio's MIME type is validated against supported types."""
        constraint = AudiosConstraint(supported_mime_types=[AudioMimeType.MP3])
        artifacts = [
            AudioArtifact(data=b"1", mime_type=AudioMimeType.MP3),
            AudioArtifact(data=b"2", mime_type=AudioMimeType.WAV),  # Invalid
        ]

        with pytest.raises(
            ConstraintViolationError, match=r"Audio 2.*mime_type must be one of"
        ):
            constraint(artifacts)

    def test_handles_empty_list(self) -> None:
        """Empty list is valid (no audios to validate)."""
        constraint = AudiosConstraint()

        result = constraint([])

        assert result == []

    def test_accepts_all_valid_audios(self) -> None:
        """All audios with valid MIME types pass validation."""
        constraint = AudiosConstraint(
            supported_mime_types=[AudioMimeType.MP3, AudioMimeType.WAV]
        )
        artifacts = [
            AudioArtifact(data=b"1", mime_type=AudioMimeType.MP3),
            AudioArtifact(data=b"2", mime_type=AudioMimeType.WAV),
        ]

        result = constraint(artifacts)

        assert result == artifacts
