"""Regression coverage for Gemini ToolsMapper — emits `parametersJsonSchema`."""

from __future__ import annotations

from celeste.providers.google.generate_content.parameters import ToolsMapper


def _map(tool: dict) -> dict:
    return ToolsMapper._map_user_tool(tool)


def test_maps_to_parameters_json_schema_not_legacy_parameters() -> None:
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
