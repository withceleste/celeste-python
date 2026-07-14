"""Google GenerateContent API tool helpers."""

import warnings
from typing import Any, ClassVar

from celeste.exceptions import UnsupportedParameterWarning
from celeste.tools import CodeExecution, Tool, ToolCall, ToolMapper, WebSearch

_NATIVE_REPLAY_PART_KEYS = {
    "codeExecutionResult",
    "executableCode",
    "functionCall",
    "toolCall",
    "toolResponse",
}


def needs_native_replay(parts: list[dict[str, Any]]) -> bool:
    """Return whether Google requires the complete Parts on the next turn."""
    return any(not _NATIVE_REPLAY_PART_KEYS.isdisjoint(part) for part in parts)


def tool_calls_from_parts(parts: list[dict[str, Any]]) -> list[ToolCall]:
    """Parse Google function-call Parts into canonical tool calls."""
    tool_calls: list[ToolCall] = []
    for part in parts:
        function_call = part.get("functionCall")
        if not isinstance(function_call, dict):
            continue
        tool_calls.append(
            ToolCall(
                id=function_call["id"],
                name=function_call["name"],
                arguments=function_call.get("args", {}),
            )
        )
    return tool_calls


class WebSearchMapper(ToolMapper):
    """Map WebSearch to Google google_search wire format."""

    tool_type = WebSearch
    _supported_fields: ClassVar[set[str]] = {"blocked_domains"}

    def map_tool(self, tool: Tool) -> dict[str, Any]:
        assert isinstance(tool, WebSearch)
        config: dict[str, Any] = {}
        if tool.blocked_domains is not None:
            config["exclude_domains"] = tool.blocked_domains
        for field in type(tool).model_fields:
            if field == "kind" or field in self._supported_fields:
                continue
            if getattr(tool, field) is not None:
                warnings.warn(
                    f"WebSearch.{field} is not supported by Google "
                    f"and will be ignored. Workaround: use a raw dict tool instead.",
                    UnsupportedParameterWarning,
                    stacklevel=2,
                )
        return {"google_search": config}


class CodeExecutionMapper(ToolMapper):
    """Map CodeExecution to Google code_execution wire format."""

    tool_type = CodeExecution

    def map_tool(self, tool: Tool) -> dict[str, Any]:
        return {"code_execution": {}}


TOOL_MAPPERS: list[ToolMapper] = [WebSearchMapper(), CodeExecutionMapper()]

__all__ = [
    "TOOL_MAPPERS",
    "CodeExecutionMapper",
    "WebSearchMapper",
    "needs_native_replay",
    "tool_calls_from_parts",
]
