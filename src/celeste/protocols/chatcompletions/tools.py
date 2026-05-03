"""Chat Completions protocol tool mappers and shared parsing helpers."""

import json
from typing import Any

from celeste.tools import ToolCall, ToolMapper

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
        raw_args = tc.get("function", {}).get("arguments")
        if isinstance(raw_args, str):
            try:
                arguments = json.loads(raw_args)
            except (json.JSONDecodeError, ValueError):
                arguments = {}
        else:
            arguments = raw_args if isinstance(raw_args, dict) else {}
        tool_calls.append(
            ToolCall(
                id=tc.get("id", ""),
                name=tc.get("function", {}).get("name", ""),
                arguments=arguments,
            )
        )
    return tool_calls


__all__ = [
    "TOOL_MAPPERS",
    "parse_tool_calls",
]
