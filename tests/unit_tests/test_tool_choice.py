"""Unit tests for ToolChoiceMapper across all protocols/providers."""

from typing import Any

import pytest

from celeste.constraints import ToolChoiceSupport
from celeste.core import Provider
from celeste.exceptions import ConstraintViolationError
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.tools import Tool, ToolChoice, WebSearch


class _UnknownTool(Tool):
    """A tool type no provider supports — for testing unsupported dispatch."""


def _make_model(provider: Provider | None = None) -> Model:
    """Create a minimal Model for testing."""
    return Model(
        id="test-model",
        provider=provider,
        display_name="Test Model",
    )


def _get_mapper(
    mappers: list[ParameterMapper[Any]], name: str = "ToolChoiceMapper"
) -> ParameterMapper[Any]:
    """Extract a mapper by class name from a parameter mappers list."""
    return next(m for m in mappers if type(m).__name__ == name)


# -- ChatCompletions protocol --


class TestChatCompletionsToolChoiceMapper:
    """Test Chat Completions tool_choice wire format."""

    @pytest.fixture
    def mapper(self) -> ParameterMapper[Any]:
        from celeste.modalities.text.protocols.chatcompletions.parameters import (
            CHATCOMPLETIONS_PARAMETER_MAPPERS,
        )

        return _get_mapper(CHATCOMPLETIONS_PARAMETER_MAPPERS)

    @pytest.fixture
    def model(self) -> Model:
        return _make_model()

    def test_none_value_is_noop(
        self, mapper: ParameterMapper[Any], model: Model
    ) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, None, model)
        assert "tool_choice" not in result

    def test_auto(self, mapper: ParameterMapper[Any], model: Model) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, ToolChoice.AUTO, model)
        assert result["tool_choice"] == "auto"

    def test_required(self, mapper: ParameterMapper[Any], model: Model) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, ToolChoice.REQUIRED, model)
        assert result["tool_choice"] == "required"

    def test_none_mode(self, mapper: ParameterMapper[Any], model: Model) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, ToolChoice.NONE, model)
        assert result["tool_choice"] == "none"

    def test_string_auto(self, mapper: ParameterMapper[Any], model: Model) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, "auto", model)
        assert result["tool_choice"] == "auto"

    def test_dict_specific_tool(
        self, mapper: ParameterMapper[Any], model: Model
    ) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, {"name": "get_weather"}, model)
        assert result["tool_choice"] == {
            "type": "function",
            "function": {"name": "get_weather"},
        }

    def test_unsupported_tool_raises(
        self, mapper: ParameterMapper[Any], model: Model
    ) -> None:
        """WebSearch is not supported in base Chat Completions (no TOOL_MAPPERS)."""
        with pytest.raises(ValueError, match="cannot be used as tool_choice"):
            mapper.map({}, _UnknownTool(), model)


# -- OpenResponses protocol --


class TestOpenResponsesToolChoiceMapper:
    """Test OpenResponses tool_choice wire format (flat structure)."""

    @pytest.fixture
    def mapper(self) -> ParameterMapper[Any]:
        from celeste.modalities.text.protocols.openresponses.parameters import (
            OPENRESPONSES_PARAMETER_MAPPERS,
        )

        return _get_mapper(OPENRESPONSES_PARAMETER_MAPPERS)

    @pytest.fixture
    def model(self) -> Model:
        return _make_model()

    def test_none_value_is_noop(
        self, mapper: ParameterMapper[Any], model: Model
    ) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, None, model)
        assert "tool_choice" not in result

    def test_auto(self, mapper: ParameterMapper[Any], model: Model) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, ToolChoice.AUTO, model)
        assert result["tool_choice"] == "auto"

    def test_required(self, mapper: ParameterMapper[Any], model: Model) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, ToolChoice.REQUIRED, model)
        assert result["tool_choice"] == "required"

    def test_none_mode(self, mapper: ParameterMapper[Any], model: Model) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, ToolChoice.NONE, model)
        assert result["tool_choice"] == "none"

    def test_dict_specific_tool(
        self, mapper: ParameterMapper[Any], model: Model
    ) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, {"name": "get_weather"}, model)
        assert result["tool_choice"] == {
            "type": "function",
            "name": "get_weather",
        }

    def test_unsupported_tool_raises(
        self, mapper: ParameterMapper[Any], model: Model
    ) -> None:
        with pytest.raises(ValueError, match="cannot be used as tool_choice"):
            mapper.map({}, _UnknownTool(), model)


# -- Anthropic Messages --


class TestAnthropicToolChoiceMapper:
    """Test Anthropic tool_choice wire format (object-based)."""

    @pytest.fixture
    def mapper(self) -> ParameterMapper[Any]:
        from celeste.modalities.text.providers.anthropic.parameters import (
            ANTHROPIC_PARAMETER_MAPPERS,
        )

        return _get_mapper(ANTHROPIC_PARAMETER_MAPPERS)

    @pytest.fixture
    def model(self) -> Model:
        return _make_model(Provider.ANTHROPIC)

    def test_none_value_is_noop(
        self, mapper: ParameterMapper[Any], model: Model
    ) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, None, model)
        assert "tool_choice" not in result

    def test_auto(self, mapper: ParameterMapper[Any], model: Model) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, ToolChoice.AUTO, model)
        assert result["tool_choice"] == {"type": "auto"}

    def test_required_maps_to_any(
        self, mapper: ParameterMapper[Any], model: Model
    ) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, ToolChoice.REQUIRED, model)
        assert result["tool_choice"] == {"type": "any"}

    def test_none_mode(self, mapper: ParameterMapper[Any], model: Model) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, ToolChoice.NONE, model)
        assert result["tool_choice"] == {"type": "none"}

    def test_dict_specific_tool(
        self, mapper: ParameterMapper[Any], model: Model
    ) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, {"name": "get_weather"}, model)
        assert result["tool_choice"] == {"type": "tool", "name": "get_weather"}

    def test_web_search_tool(self, mapper: ParameterMapper[Any], model: Model) -> None:
        """Anthropic supports WebSearch — dispatches through TOOL_MAPPERS."""
        request: dict[str, Any] = {}
        result = mapper.map(request, WebSearch(), model)
        assert result["tool_choice"] == {"type": "tool", "name": "web_search"}


# -- Google GenerateContent --


class TestGoogleToolChoiceMapper:
    """Test Google toolConfig.functionCallingConfig wire format."""

    @pytest.fixture
    def mapper(self) -> ParameterMapper[Any]:
        from celeste.modalities.text.providers.google.parameters import (
            GOOGLE_PARAMETER_MAPPERS,
        )

        return _get_mapper(GOOGLE_PARAMETER_MAPPERS)

    @pytest.fixture
    def model(self) -> Model:
        return _make_model(Provider.GOOGLE)

    def test_none_value_is_noop(
        self, mapper: ParameterMapper[Any], model: Model
    ) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, None, model)
        assert "toolConfig" not in result

    def test_auto(self, mapper: ParameterMapper[Any], model: Model) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, ToolChoice.AUTO, model)
        assert result["toolConfig"]["functionCallingConfig"] == {"mode": "AUTO"}

    def test_required_maps_to_any(
        self, mapper: ParameterMapper[Any], model: Model
    ) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, ToolChoice.REQUIRED, model)
        assert result["toolConfig"]["functionCallingConfig"] == {"mode": "ANY"}

    def test_none_mode(self, mapper: ParameterMapper[Any], model: Model) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, ToolChoice.NONE, model)
        assert result["toolConfig"]["functionCallingConfig"] == {"mode": "NONE"}

    def test_dict_specific_tool(
        self, mapper: ParameterMapper[Any], model: Model
    ) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, {"name": "get_weather"}, model)
        assert result["toolConfig"]["functionCallingConfig"] == {
            "mode": "ANY",
            "allowedFunctionNames": ["get_weather"],
        }


# -- Mistral override --


class TestMistralToolChoiceMapper:
    """Test Mistral translates 'required' to 'any'."""

    @pytest.fixture
    def mapper(self) -> ParameterMapper[Any]:
        from celeste.modalities.text.providers.mistral.parameters import (
            MISTRAL_PARAMETER_MAPPERS,
        )

        return _get_mapper(MISTRAL_PARAMETER_MAPPERS)

    @pytest.fixture
    def model(self) -> Model:
        return _make_model(Provider.MISTRAL)

    def test_required_becomes_any(
        self, mapper: ParameterMapper[Any], model: Model
    ) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, ToolChoice.REQUIRED, model)
        assert result["tool_choice"] == "any"

    def test_auto_unchanged(self, mapper: ParameterMapper[Any], model: Model) -> None:
        request: dict[str, Any] = {}
        result = mapper.map(request, ToolChoice.AUTO, model)
        assert result["tool_choice"] == "auto"


# -- ToolChoiceSupport constraint --


class TestToolChoiceSupport:
    """Test ToolChoiceSupport constraint validation."""

    def test_valid_mode_passes(self) -> None:
        constraint = ToolChoiceSupport(modes=["auto", "required", "none"])
        assert constraint("auto") == "auto"
        assert constraint("required") == "required"
        assert constraint("none") == "none"

    def test_invalid_mode_raises(self) -> None:
        constraint = ToolChoiceSupport(modes=["auto", "none"])
        with pytest.raises(ConstraintViolationError, match="not supported"):
            constraint("required")

    def test_tool_instance_passes_through(self) -> None:
        constraint = ToolChoiceSupport(modes=["auto", "required", "none"])
        ws = WebSearch()
        assert constraint(ws) is ws

    def test_dict_passes_through(self) -> None:
        constraint = ToolChoiceSupport(modes=["auto", "required", "none"])
        d = {"name": "get_weather"}
        assert constraint(d) is d

    def test_tool_choice_enum_validated_as_string(self) -> None:
        constraint = ToolChoiceSupport(modes=["auto", "none"])
        assert constraint(ToolChoice.AUTO) == "auto"
        with pytest.raises(ConstraintViolationError, match="not supported"):
            constraint(ToolChoice.REQUIRED)
