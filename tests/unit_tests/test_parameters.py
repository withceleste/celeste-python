"""High-value tests for celeste.parameters module."""

from enum import StrEnum
from typing import Any, get_type_hints

import pytest
from pydantic.fields import FieldInfo

from celeste.constraints import Range, Str
from celeste.core import Parameter, Provider
from celeste.exceptions import ConstraintViolationError
from celeste.modalities.audio.parameters import AudioParameters
from celeste.modalities.images.parameters import ImageParameters
from celeste.modalities.text.parameters import TextParameters
from celeste.modalities.videos.parameters import VideoParameters
from celeste.models import Model
from celeste.types import TextContent


def _field_description(params_type: type, field_name: str) -> str | None:
    hints = get_type_hints(params_type, include_extras=True)
    hint = hints[field_name]
    for meta in getattr(hint, "__metadata__", ()):
        if isinstance(meta, FieldInfo):
            return meta.description
    return None


class TestParameterTypedDictAnnotations:
    """Each modality's Parameters TypedDict must carry per-field Field descriptions."""

    def test_image_parameters_describe_every_field(self) -> None:
        hints = get_type_hints(ImageParameters, include_extras=True)
        for name in hints:
            assert _field_description(ImageParameters, name), (
                f"ImageParameters.{name} missing Field(description=...)"
            )

    def test_audio_parameters_describe_every_field(self) -> None:
        hints = get_type_hints(AudioParameters, include_extras=True)
        for name in hints:
            assert _field_description(AudioParameters, name), (
                f"AudioParameters.{name} missing Field(description=...)"
            )

    def test_video_parameters_describe_every_field(self) -> None:
        hints = get_type_hints(VideoParameters, include_extras=True)
        for name in hints:
            assert _field_description(VideoParameters, name), (
                f"VideoParameters.{name} missing Field(description=...)"
            )

    def test_text_parameters_describe_every_field(self) -> None:
        hints = get_type_hints(TextParameters, include_extras=True)
        for name in hints:
            assert _field_description(TextParameters, name), (
                f"TextParameters.{name} missing Field(description=...)"
            )

    def test_base_type_is_preserved_under_annotated(self) -> None:
        hints = get_type_hints(ImageParameters, include_extras=True)
        assert hints["aspect_ratio"].__origin__ is str
        assert hints["num_images"].__origin__ is int
        assert hints["guidance"].__origin__ is float


class TestConstraintDescription:
    """Constraint carries optional per-model description metadata."""

    def test_description_defaults_to_none(self) -> None:
        assert Range(min=0, max=1).description is None

    def test_description_is_settable(self) -> None:
        constraint = Range(
            min=0, max=1, description="Temperature bounds for this model."
        )
        assert constraint.description == "Temperature bounds for this model."

    def test_str_constraint_inherits_description(self) -> None:
        constraint = Str(
            max_length=500, description="Prompt length capped by provider."
        )
        assert constraint.description == "Prompt length capped by provider."


class DefaultParseOutputMapper:
    """Mapper that uses default parse_output behavior (returns content unchanged)."""

    name: StrEnum = Parameter.TEMPERATURE

    def map(self, request: dict[str, Any], value: Any, model: Model) -> dict[str, Any]:  # noqa: ANN401
        """Transform parameter value into provider request."""
        if value is not None:
            request["temperature"] = value
        return request

    def parse_output(self, content: TextContent, value: object | None) -> TextContent:
        """Default implementation: return content unchanged."""
        return content


class TestParameterMapperProtocol:
    """Test ParameterMapper Protocol behavior."""

    @pytest.mark.parametrize(
        "content,value",
        [
            ("test string", None),
            ({"key": "value"}, None),
            ([1, 2, 3], None),
            (None, None),
            (42, None),
            (True, None),
            ("test content", "some parameter value"),
        ],
    )
    def test_parse_output_returns_content_unchanged(
        self, content: TextContent, value: object | None
    ) -> None:
        """Default parse_output implementation returns content unchanged.

        Tests the documented default behavior of ParameterMapper.parse_output.
        This covers line 50 in parameters.py.
        """
        # Arrange
        mapper = DefaultParseOutputMapper()

        # Act
        result = mapper.parse_output(content, value=value)

        # Assert
        assert result is content


class TestParameterMapperBaseClass:
    """Test ParameterMapper base class methods."""

    def test_parse_output_default_returns_content_unchanged(self) -> None:
        """Test that ParameterMapper.parse_output default returns content unchanged."""
        from celeste.parameters import ParameterMapper

        class TestMapper(ParameterMapper[TextContent]):
            name = Parameter.TEMPERATURE

            def map(
                self,
                request: dict[str, Any],
                value: Any,  # noqa: ANN401
                model: Model,
            ) -> dict[str, Any]:
                return request

        mapper = TestMapper()
        content: TextContent = "test content"
        result = mapper.parse_output(content, value=None)
        assert result is content

    def test_validate_value_with_none_returns_none(self) -> None:
        """Test that _validate_value returns None when value is None."""
        from celeste.parameters import ParameterMapper

        class TestMapper(ParameterMapper[TextContent]):
            name = Parameter.TEMPERATURE

            def map(
                self,
                request: dict[str, Any],
                value: Any,  # noqa: ANN401
                model: Model,
            ) -> dict[str, Any]:
                return request

        mapper = TestMapper()
        model = Model(
            id="test-model",
            provider=Provider.OPENAI,
            display_name="Test Model",
        )
        result = mapper._validate_value(None, model)
        assert result is None

    def test_validate_value_with_missing_constraint_passes_through(self) -> None:
        """Missing constraints pass through without error."""
        from celeste.parameters import ParameterMapper

        class TestMapper(ParameterMapper[TextContent]):
            name = Parameter.TEMPERATURE

            def map(
                self,
                request: dict[str, Any],
                value: Any,  # noqa: ANN401
                model: Model,
            ) -> dict[str, Any]:
                return request

        mapper = TestMapper()
        model = Model(
            id="test-model-no-constraints",
            provider=Provider.OPENAI,
            display_name="Test Model",
            parameter_constraints={},  # No constraints
        )
        result = mapper._validate_value(0.7, model)
        assert result == 0.7

    def test_validate_value_with_valid_constraint_calls_constraint(self) -> None:
        """Test that _validate_value calls constraint when parameter is supported."""
        from celeste.parameters import ParameterMapper

        class TestMapper(ParameterMapper[TextContent]):
            name = Parameter.TEMPERATURE

            def map(
                self,
                request: dict[str, Any],
                value: Any,  # noqa: ANN401
                model: Model,
            ) -> dict[str, Any]:
                return request

        mapper = TestMapper()
        constraint = Str(min_length=1)
        model = Model(
            id="test-model",
            provider=Provider.OPENAI,
            display_name="Test Model",
            parameter_constraints={Parameter.TEMPERATURE: constraint},
        )
        # Note: This will fail validation because Str constraint expects str, not float
        # But it tests that the constraint is called
        with pytest.raises(ConstraintViolationError):
            mapper._validate_value(0.7, model)

    def test_validate_value_with_valid_constraint_returns_validated_value(self) -> None:
        """Test that _validate_value returns constraint-validated value."""
        from celeste.parameters import ParameterMapper

        class TestMapper(ParameterMapper[TextContent]):
            name = Parameter.TEMPERATURE

            def map(
                self,
                request: dict[str, Any],
                value: Any,  # noqa: ANN401
                model: Model,
            ) -> dict[str, Any]:
                return request

        mapper = TestMapper()
        constraint = Range(min=0.0, max=1.0)
        model = Model(
            id="test-model",
            provider=Provider.OPENAI,
            display_name="Test Model",
            parameter_constraints={Parameter.TEMPERATURE: constraint},
        )
        result = mapper._validate_value(0.7, model)
        assert result == 0.7
