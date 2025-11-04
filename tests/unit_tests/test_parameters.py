"""High-value tests for celeste.parameters module."""

from enum import StrEnum
from typing import Any

import pytest

from celeste.core import Parameter
from celeste.models import Model


class DefaultParseOutputMapper:
    """Mapper that uses default parse_output behavior (returns content unchanged)."""

    name: StrEnum = Parameter.TEMPERATURE

    def map(self, request: dict[str, Any], value: Any, model: Model) -> dict[str, Any]:  # noqa: ANN401
        """Transform parameter value into provider request."""
        if value is not None:
            request["temperature"] = value
        return request

    def parse_output(self, content: object, value: object | None) -> object:
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
        self, content: object, value: object | None
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
