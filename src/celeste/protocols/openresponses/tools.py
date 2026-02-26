"""OpenResponses protocol tool mappers."""

from typing import Any

from celeste.tools import CodeExecution, Tool, ToolMapper, WebSearch, XSearch


class WebSearchMapper(ToolMapper):
    """Map WebSearch to OpenResponses web_search wire format."""

    tool_type = WebSearch

    def map_tool(self, tool: Tool) -> dict[str, Any]:
        assert isinstance(tool, WebSearch)
        result: dict[str, Any] = {"type": "web_search"}
        if tool.allowed_domains is not None:
            result.setdefault("filters", {})["allowed_domains"] = tool.allowed_domains
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

__all__ = [
    "TOOL_MAPPERS",
    "CodeExecutionMapper",
    "WebSearchMapper",
    "XSearchMapper",
]
