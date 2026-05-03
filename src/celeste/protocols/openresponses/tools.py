"""OpenResponses protocol tool mappers and shared parsing helpers."""

import json
import warnings
from typing import Any, ClassVar

from celeste.exceptions import UnsupportedParameterWarning
from celeste.tools import (
    CodeExecution,
    Tool,
    ToolCall,
    ToolMapper,
    WebSearch,
    XSearch,
)


class WebSearchMapper(ToolMapper):
    """Map WebSearch to OpenResponses web_search wire format."""

    tool_type = WebSearch
    _supported_fields: ClassVar[set[str]] = {"allowed_domains"}

    def map_tool(self, tool: Tool) -> dict[str, Any]:
        assert isinstance(tool, WebSearch)
        result: dict[str, Any] = {"type": "web_search"}
        if tool.allowed_domains is not None:
            result.setdefault("filters", {})["allowed_domains"] = tool.allowed_domains
        for field in type(tool).model_fields:
            if field not in self._supported_fields and getattr(tool, field) is not None:
                warnings.warn(
                    f"WebSearch.{field} is not supported by OpenResponses "
                    f"and will be ignored. Workaround: use a raw dict tool instead.",
                    UnsupportedParameterWarning,
                    stacklevel=2,
                )
        return result


class XSearchMapper(ToolMapper):
    """Map XSearch to OpenResponses x_search wire format."""

    tool_type = XSearch

    def map_tool(self, tool: Tool) -> dict[str, Any]:
        return {"type": "x_search"}


class CodeExecutionMapper(ToolMapper):
    """Map CodeExecution to OpenResponses code_execution wire format."""

    tool_type = CodeExecution

    def map_tool(self, tool: Tool) -> dict[str, Any]:
        return {"type": "code_execution"}


TOOL_MAPPERS: list[ToolMapper] = [
    WebSearchMapper(),
    XSearchMapper(),
    CodeExecutionMapper(),
]


def parse_tool_calls(response_data: dict[str, Any]) -> list[ToolCall]:
    """Parse tool calls from Responses API output."""
    tool_calls: list[ToolCall] = []
    for item in response_data.get("output", []):
        if item.get("type") != "function_call":
            continue
        raw_args = item.get("arguments")
        if isinstance(raw_args, str):
            try:
                arguments = json.loads(raw_args)
            except (json.JSONDecodeError, ValueError):
                arguments = {}
        else:
            arguments = raw_args if isinstance(raw_args, dict) else {}
        tool_calls.append(
            ToolCall(
                id=item.get("call_id", item.get("id", "")),
                name=item.get("name", ""),
                arguments=arguments,
            )
        )
    return tool_calls


def parse_content(output: list[dict[str, Any]]) -> str:
    """Extract text from Responses API output items."""
    for item in output:
        if item.get("type") == "message":
            for part in item.get("content", []):
                if part.get("type") == "output_text":
                    return part.get("text") or ""
    return ""


def parse_reasoning(
    output: list[dict[str, Any]],
) -> tuple[str | None, list[dict[str, Any]]]:
    """Extract reasoning from Responses API output items."""
    reasoning_parts: list[str] = []
    signature_blocks: list[dict[str, Any]] = []
    for item in output:
        if item.get("type") == "reasoning":
            signature_blocks.append(item)
            for s in item.get("summary", []):
                if s.get("type") == "summary_text":
                    text = s.get("text", "")
                    if text:
                        reasoning_parts.append(text)
            for c in item.get("content", []):
                if c.get("type") == "reasoning_text":
                    text = c.get("text", "")
                    if text:
                        reasoning_parts.append(text)
    text = "\n".join(reasoning_parts) if reasoning_parts else None
    return text, signature_blocks


__all__ = [
    "TOOL_MAPPERS",
    "CodeExecutionMapper",
    "WebSearchMapper",
    "XSearchMapper",
    "parse_content",
    "parse_reasoning",
    "parse_tool_calls",
]
