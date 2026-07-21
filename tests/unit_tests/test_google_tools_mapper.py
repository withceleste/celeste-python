"""Regression coverage for Gemini ToolsMapper."""

from __future__ import annotations

from typing import Any

import pytest

from celeste.core import Provider
from celeste.modalities.text.parameters import TextParameter
from celeste.models import Model
from celeste.providers.google.generate_content.parameters import ToolsMapper
from celeste.providers.google.interactions.parameters import (
    ToolsMapper as InteractionsToolsMapper,
)
from celeste.tools import CodeExecution, ToolDefinition, UrlContext, WebSearch


class _GoogleToolsMapper(ToolsMapper):
    name = TextParameter.TOOLS


class _GoogleInteractionsToolsMapper(InteractionsToolsMapper):
    name = TextParameter.TOOLS


_MAPPER = _GoogleToolsMapper()
_MODEL = Model(id="test-model", provider=Provider.GOOGLE, display_name="Test Model")
_FUNCTION_TOOL: dict[str, Any] = {
    "name": "web_fetch",
    "parameters": {"type": "object"},
}


def _map(tool: dict) -> dict:
    return ToolsMapper._map_user_tool(tool)


def _map_tools(tools: list[ToolDefinition]) -> dict[str, Any]:
    return _MAPPER.map({}, tools, _MODEL)


def test_url_context_maps_to_both_wire_shapes() -> None:
    assert _map_tools([UrlContext()])["tools"] == [{"url_context": {}}]
    interactions = _GoogleInteractionsToolsMapper().map({}, [UrlContext()], _MODEL)
    assert interactions["tools"] == [{"type": "url_context"}]


def test_maps_to_parameters_json_schema() -> None:
    fn = _map(
        {
            "name": "example",
            "description": "example tool",
            "parameters": {
                "type": "object",
                "properties": {"prompt": {"type": "string"}},
                "required": ["prompt"],
            },
        },
    )
    assert "parametersJsonSchema" in fn
    assert "parameters" not in fn
    assert fn["parametersJsonSchema"]["properties"]["prompt"]["type"] == "string"


def test_preserves_integer_enum_on_non_string_type() -> None:
    fn = _map(
        {
            "name": "example",
            "parameters": {
                "type": "object",
                "properties": {
                    "duration": {"type": "integer", "enum": [4, 6, 8]},
                },
            },
        },
    )
    duration = fn["parametersJsonSchema"]["properties"]["duration"]
    assert duration["type"] == "integer"
    assert duration["enum"] == [4, 6, 8]


def test_preserves_title_fields() -> None:
    fn = _map(
        {
            "name": "example",
            "parameters": {
                "title": "ExampleInput",
                "type": "object",
                "properties": {"x": {"type": "string", "title": "X"}},
            },
        },
    )
    assert fn["parametersJsonSchema"]["title"] == "ExampleInput"
    assert fn["parametersJsonSchema"]["properties"]["x"]["title"] == "X"


def test_tool_with_no_parameters_emits_no_schema_field() -> None:
    fn = _map({"name": "example", "description": "no-args"})
    assert "parameters" not in fn
    assert "parametersJsonSchema" not in fn
    assert fn["description"] == "no-args"


@pytest.mark.parametrize(
    ("tools", "expect_flag"),
    [
        ([WebSearch(), _FUNCTION_TOOL], True),
        ([CodeExecution(), _FUNCTION_TOOL], True),
        ([{"google_search": {}}, _FUNCTION_TOOL], True),
        ([_FUNCTION_TOOL], False),
        ([WebSearch()], False),
        ([CodeExecution()], False),
    ],
)
def test_include_server_side_tool_invocations(
    tools: list[ToolDefinition], expect_flag: bool
) -> None:
    result = _map_tools(tools)
    flag = result.get("toolConfig", {}).get("includeServerSideToolInvocations")
    if expect_flag:
        assert flag is True
        assert any("functionDeclarations" in tool for tool in result["tools"])
    else:
        assert flag is None
