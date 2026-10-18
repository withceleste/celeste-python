"""Tool-choice wire formats and model constraints."""

from typing import Any

import pytest

from celeste.constraints import ToolChoiceSupport
from celeste.core import Provider
from celeste.exceptions import ConstraintViolationError
from celeste.modalities.text.parameters import TextParameter
from celeste.modalities.text.protocols.chatcompletions.parameters import (
    CHATCOMPLETIONS_PARAMETER_MAPPERS,
)
from celeste.modalities.text.protocols.openresponses.parameters import (
    OPENRESPONSES_PARAMETER_MAPPERS,
)
from celeste.modalities.text.providers.anthropic.parameters import (
    ANTHROPIC_PARAMETER_MAPPERS,
)
from celeste.modalities.text.providers.google.parameters import (
    GOOGLE_INTERACTIONS_PARAMETER_MAPPERS,
    GOOGLE_VERTEX_PARAMETER_MAPPERS,
)
from celeste.modalities.text.providers.mistral.parameters import (
    MISTRAL_PARAMETER_MAPPERS,
)
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.tools import Tool, ToolChoice, WebSearch


class _UnknownTool(Tool):
    pass


def _mapper(mappers: list[ParameterMapper[Any]]) -> ParameterMapper[Any]:
    return next(
        mapper for mapper in mappers if mapper.name == TextParameter.TOOL_CHOICE
    )


def _map(
    mappers: list[ParameterMapper[Any]],
    value: object,
    provider: Provider | None = None,
) -> dict[str, Any]:
    model = Model(id="test", provider=provider, display_name="test")
    return _mapper(mappers).map({}, value, model)


@pytest.mark.parametrize(
    ("mappers", "provider", "value", "expected"),
    [
        (
            CHATCOMPLETIONS_PARAMETER_MAPPERS,
            None,
            ToolChoice.AUTO,
            {"tool_choice": "auto"},
        ),
        (
            CHATCOMPLETIONS_PARAMETER_MAPPERS,
            None,
            ToolChoice.REQUIRED,
            {"tool_choice": "required"},
        ),
        (
            OPENRESPONSES_PARAMETER_MAPPERS,
            None,
            ToolChoice.NONE,
            {"tool_choice": "none"},
        ),
        (
            ANTHROPIC_PARAMETER_MAPPERS,
            Provider.ANTHROPIC,
            ToolChoice.AUTO,
            {"tool_choice": {"type": "auto"}},
        ),
        (
            ANTHROPIC_PARAMETER_MAPPERS,
            Provider.ANTHROPIC,
            ToolChoice.REQUIRED,
            {"tool_choice": {"type": "any"}},
        ),
        (
            ANTHROPIC_PARAMETER_MAPPERS,
            Provider.ANTHROPIC,
            ToolChoice.NONE,
            {"tool_choice": {"type": "none"}},
        ),
        (
            GOOGLE_VERTEX_PARAMETER_MAPPERS,
            Provider.GOOGLE,
            ToolChoice.AUTO,
            {"toolConfig": {"functionCallingConfig": {"mode": "AUTO"}}},
        ),
        (
            GOOGLE_VERTEX_PARAMETER_MAPPERS,
            Provider.GOOGLE,
            ToolChoice.REQUIRED,
            {"toolConfig": {"functionCallingConfig": {"mode": "ANY"}}},
        ),
        (
            GOOGLE_VERTEX_PARAMETER_MAPPERS,
            Provider.GOOGLE,
            ToolChoice.NONE,
            {"toolConfig": {"functionCallingConfig": {"mode": "NONE"}}},
        ),
        (
            MISTRAL_PARAMETER_MAPPERS,
            Provider.MISTRAL,
            ToolChoice.REQUIRED,
            {"tool_choice": "any"},
        ),
    ],
)
def test_choice_wire_format(
    mappers: list[ParameterMapper[Any]],
    provider: Provider | None,
    value: ToolChoice,
    expected: dict[str, Any],
) -> None:
    assert _map(mappers, value, provider) == expected


@pytest.mark.parametrize(
    ("tools", "expected"),
    [
        ([{"type": "google_search"}, {"name": "weather"}], "validated"),
        ([{"name": "weather"}], "auto"),
        ([{"type": "google_search"}], "auto"),
    ],
)
def test_google_interactions_auto_choice_for_tool_mix(
    tools: list[object], expected: str
) -> None:
    request: dict[str, Any] = {}
    parameters: dict[Any, object] = {
        TextParameter.TOOLS: tools,
        TextParameter.TOOL_CHOICE: ToolChoice.AUTO,
    }
    model = Model(id="test", provider=Provider.GOOGLE, display_name="test")

    for mapper in GOOGLE_INTERACTIONS_PARAMETER_MAPPERS:
        request = mapper.map(request, parameters.get(mapper.name), model)

    assert request["generation_config"]["tool_choice"] == expected


@pytest.mark.parametrize(
    ("mappers", "provider", "expected"),
    [
        (
            CHATCOMPLETIONS_PARAMETER_MAPPERS,
            None,
            {"type": "function", "function": {"name": "weather"}},
        ),
        (
            OPENRESPONSES_PARAMETER_MAPPERS,
            None,
            {"type": "function", "name": "weather"},
        ),
        (
            ANTHROPIC_PARAMETER_MAPPERS,
            Provider.ANTHROPIC,
            {"type": "tool", "name": "weather"},
        ),
        (
            GOOGLE_VERTEX_PARAMETER_MAPPERS,
            Provider.GOOGLE,
            {"mode": "ANY", "allowedFunctionNames": ["weather"]},
        ),
    ],
)
def test_specific_tool_wire_format(
    mappers: list[ParameterMapper[Any]],
    provider: Provider | None,
    expected: dict[str, Any],
) -> None:
    request = _map(mappers, {"name": "weather"}, provider)
    actual = (
        request["toolConfig"]["functionCallingConfig"]
        if provider == Provider.GOOGLE
        else request["tool_choice"]
    )
    assert actual == expected


def test_anthropic_maps_server_tool_choice() -> None:
    assert _map(ANTHROPIC_PARAMETER_MAPPERS, WebSearch(), Provider.ANTHROPIC) == {
        "tool_choice": {"type": "tool", "name": "web_search"}
    }


def test_unsupported_tool_choice_fails() -> None:
    with pytest.raises(ValueError, match="cannot be used as tool_choice"):
        _map(CHATCOMPLETIONS_PARAMETER_MAPPERS, _UnknownTool())


@pytest.mark.parametrize(
    "value", ["auto", ToolChoice.NONE, {"name": "weather"}, WebSearch()]
)
def test_constraint_accepts_supported_shapes(value: object) -> None:
    assert ToolChoiceSupport(modes=["auto", "none"])(value) == value


def test_constraint_rejects_unsupported_mode() -> None:
    with pytest.raises(ConstraintViolationError, match="not supported"):
        ToolChoiceSupport(modes=["auto"])(ToolChoice.REQUIRED)
