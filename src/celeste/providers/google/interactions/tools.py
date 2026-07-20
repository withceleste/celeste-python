"""Google Interactions API tool helpers."""

import warnings
from typing import Any, ClassVar
from uuid import uuid4

from celeste.exceptions import UnsupportedParameterWarning
from celeste.tools import (
    CodeExecution,
    Tool,
    ToolCall,
    ToolMapper,
    UrlContext,
    WebSearch,
)


def tool_calls_from_steps(steps: list[dict[str, Any]]) -> list[ToolCall]:
    """Extract tool calls from a completed or reconstructed steps array."""
    tool_calls: list[ToolCall] = []
    for step in steps:
        if step.get("type") != "function_call":
            continue
        kwargs: dict[str, Any] = {}
        if step.get("signature"):
            kwargs["signature"] = step["signature"]
        tool_calls.append(
            ToolCall(
                id=step.get("id") or str(uuid4()),
                name=step["name"],
                arguments=step.get("arguments", {}),
                **kwargs,
            )
        )
    return tool_calls


class WebSearchMapper(ToolMapper):
    """Map WebSearch to Google Interactions google_search wire format."""

    tool_type = WebSearch
    _supported_fields: ClassVar[set[str]] = {"blocked_domains"}

    def map_tool(self, tool: Tool) -> dict[str, Any]:
        assert isinstance(tool, WebSearch)
        result: dict[str, Any] = {"type": "google_search"}
        if tool.blocked_domains is not None:
            result["exclude_domains"] = tool.blocked_domains
        for field in type(tool).model_fields:
            if field not in self._supported_fields and getattr(tool, field) is not None:
                warnings.warn(
                    f"WebSearch.{field} is not supported by Google "
                    f"and will be ignored. Workaround: use a raw dict tool instead.",
                    UnsupportedParameterWarning,
                    stacklevel=2,
                )
        return result


class CodeExecutionMapper(ToolMapper):
    """Map CodeExecution to Google Interactions code_execution wire format."""

    tool_type = CodeExecution

    def map_tool(self, tool: Tool) -> dict[str, Any]:
        return {"type": "code_execution"}


class UrlContextMapper(ToolMapper):
    """Map UrlContext to Google Interactions url_context wire format."""

    tool_type = UrlContext

    def map_tool(self, tool: Tool) -> dict[str, Any]:
        return {"type": "url_context"}


TOOL_MAPPERS: list[ToolMapper] = [
    WebSearchMapper(),
    CodeExecutionMapper(),
    UrlContextMapper(),
]

__all__ = [
    "TOOL_MAPPERS",
    "CodeExecutionMapper",
    "UrlContextMapper",
    "WebSearchMapper",
    "tool_calls_from_steps",
]
