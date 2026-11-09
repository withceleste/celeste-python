"""Chat Completions protocol tool mappers and shared parsing helpers."""

from typing import Any

from celeste.tools import ToolCall, ToolMapper, _parse_tool_arguments

TOOL_MAPPERS: list[ToolMapper] = []


def parse_tool_calls(
    response_data: dict[str, Any],
) -> list[ToolCall]:
    """Parse tool calls from Chat Completions API response."""
    choices = response_data.get("choices", [])
    if not choices:
        return []

    message = choices[0].get("message", {})
    raw_tool_calls = message.get("tool_calls")
    if not raw_tool_calls:
        return []

    tool_calls: list[ToolCall] = []
    for tc in raw_tool_calls:
        function = tc.get("function", {})
        arguments = _parse_tool_arguments(
            function.get("arguments"), name=function.get("name", "")
        )
        tool_calls.append(
            ToolCall(
                id=tc.get("id", ""),
                name=function.get("name", ""),
                arguments=arguments,
            )
        )
    return tool_calls


def parse_annotations(response_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract citation/search annotations from the Chat Completions message."""
    choices = response_data.get("choices", [])
    if not choices:
        return []

    message = choices[0].get("message", {})
    message_annotations = message.get("annotations")
    if not isinstance(message_annotations, list):
        return []

    return [
        annotation for annotation in message_annotations if isinstance(annotation, dict)
    ]


__all__ = [
    "TOOL_MAPPERS",
    "parse_annotations",
    "parse_tool_calls",
]
