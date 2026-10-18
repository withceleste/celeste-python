"""Tool-choice wire formats and model constraints."""

from typing import Any, ClassVar

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
from celeste.modalities.text.providers.openai.parameters import (
    OPENAI_PARAMETER_MAPPERS,
)
from celeste.modalities.text.providers.xai.parameters import XAI_PARAMETER_MAPPERS
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.protocols.openresponses.parameters import (
    ToolChoiceMapper as ResponsesToolChoiceMapper,
)
from celeste.tools import (
    CodeExecution,
    Tool,
    ToolChoice,
    ToolMapper,
    UrlContext,
    WebSearch,
    XSearch,
)


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


@pytest.mark.parametrize(
    ("mappers", "provider"),
    [
        (OPENRESPONSES_PARAMETER_MAPPERS, None),
        (XAI_PARAMETER_MAPPERS, Provider.XAI),
        (GOOGLE_INTERACTIONS_PARAMETER_MAPPERS, Provider.GOOGLE),
        (GOOGLE_VERTEX_PARAMETER_MAPPERS, Provider.GOOGLE),
    ],
)
@pytest.mark.parametrize(
    "tool", [WebSearch(), XSearch(), CodeExecution(), UrlContext(), _UnknownTool()]
)
def test_native_tool_choices_require_provider_support(
    mappers: list[ParameterMapper[Any]], provider: Provider | None, tool: Tool
) -> None:
    with pytest.raises(ValueError, match="cannot be used as tool_choice"):
        _map(mappers, tool, provider)


@pytest.mark.parametrize(
    "tool", [XSearch(), CodeExecution(), UrlContext(), _UnknownTool()]
)
def test_openai_rejects_unsupported_native_tool_choices(tool: Tool) -> None:
    with pytest.raises(ValueError, match="cannot be used as tool_choice"):
        _map(OPENAI_PARAMETER_MAPPERS, tool, Provider.OPENAI)


def test_openai_forces_web_search_without_changing_declared_tools() -> None:
    request: dict[str, Any] = {}
    parameters: dict[Any, object] = {
        TextParameter.TOOLS: [
            WebSearch(allowed_domains=["example.com"]),
            {"name": "weather"},
        ],
        TextParameter.TOOL_CHOICE: WebSearch(allowed_domains=["example.com"]),
    }
    model = Model(id="test", provider=Provider.OPENAI, display_name="test")
    for mapper in OPENAI_PARAMETER_MAPPERS:
        request = mapper.map(request, parameters.get(mapper.name), model)
    assert request["tools"] == [
        {"type": "web_search", "filters": {"allowed_domains": ["example.com"]}},
        {"type": "function", "name": "weather"},
    ]
    assert request["tool_choice"] == {
        "type": "allowed_tools",
        "mode": "required",
        "tools": [{"type": "web_search"}],
    }
    assert (
        sum(
            mapper.name == TextParameter.TOOL_CHOICE
            for mapper in OPENAI_PARAMETER_MAPPERS
        )
        == 1
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, {}),
        (ToolChoice.AUTO, {"tool_choice": "auto"}),
        (ToolChoice.REQUIRED, {"tool_choice": "required"}),
        (ToolChoice.NONE, {"tool_choice": "none"}),
        ({"name": "weather"}, {"tool_choice": {"type": "function", "name": "weather"}}),
        ({"type": "code_interpreter"}, {"tool_choice": {"type": "code_interpreter"}}),
    ],
)
def test_openai_preserves_other_tool_choices(
    value: object, expected: dict[str, Any]
) -> None:
    assert _map(OPENAI_PARAMETER_MAPPERS, value, Provider.OPENAI) == expected


def test_google_interactions_preserves_named_function_choice() -> None:
    assert _map(
        GOOGLE_INTERACTIONS_PARAMETER_MAPPERS, {"name": "weather"}, Provider.GOOGLE
    ) == {
        "generation_config": {
            "tool_choice": {"allowed_tools": {"mode": "any", "tools": ["weather"]}}
        }
    }


@pytest.mark.parametrize(
    "wire",
    [
        {"type": "web_search", "name": "search"},
        {"name": "weather"},
        {"type": "function", "name": None},
        {"type": "function", "name": ""},
        {"type": "function", "name": 1},
    ],
)
def test_portable_choice_rejects_non_function_or_invalid_names(
    wire: dict[str, Any],
) -> None:
    class MappedTool(ToolMapper):
        tool_type = _UnknownTool

        def map_tool(self, tool: Tool) -> dict[str, Any]:
            return wire

    class MappedChoice(ResponsesToolChoiceMapper):
        name = TextParameter.TOOL_CHOICE
        _tool_mappers: ClassVar[list[ToolMapper]] = [MappedTool()]

    model = Model(id="test", display_name="test")
    with pytest.raises(ValueError, match="cannot be used as tool_choice"):
        MappedChoice().map({}, _UnknownTool(), model)


def test_portable_choice_uses_effective_function_mapper() -> None:
    class MappedTool(ToolMapper):
        tool_type = _UnknownTool

        def map_tool(self, tool: Tool) -> dict[str, Any]:
            return {"type": "function", "name": "weather", "description": "Weather"}

    class MappedChoice(ResponsesToolChoiceMapper):
        name = TextParameter.TOOL_CHOICE
        _tool_mappers: ClassVar[list[ToolMapper]] = [MappedTool()]

    model = Model(id="test", display_name="test")
    assert MappedChoice().map({}, _UnknownTool(), model) == {
        "tool_choice": {"type": "function", "name": "weather"}
    }
