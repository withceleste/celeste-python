"""Chat Completions protocol tool mappers and shared parsing helpers."""

import json
from typing import Any

from celeste.tools import ToolCall, ToolMapper, ToolResult
from celeste.types import Message

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


def serialize_messages(
    messages: list[Message],
) -> list[dict[str, Any]]:
    """Serialize messages to Chat Completions API format."""
    items: list[dict[str, Any]] = []
    for msg in messages:
        if isinstance(msg, ToolResult):
            items.append(
                {
                    "role": "tool",
                    "tool_call_id": msg.tool_call_id,
                    "content": str(msg.content),
                }
            )
        elif msg.role == "assistant" and msg.tool_calls:
            msg_dict = msg.model_dump(exclude_none=True)
            msg_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": json.dumps(tc.arguments),
                    },
                }
                for tc in msg.tool_calls
            ]
            items.append(msg_dict)
        else:
            msg_dict = msg.model_dump(exclude_none=True)
            msg_dict.pop("tool_calls", None)
            items.append(msg_dict)
    return items


__all__ = [
    "TOOL_MAPPERS",
    "parse_tool_calls",
    "serialize_messages",
]
