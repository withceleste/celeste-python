"""XAI Responses API tool mappers."""

from typing import Any

from celeste.protocols.openresponses.tools import WebSearchMapper
from celeste.tools import CodeExecution, Tool, ToolMapper, XSearch


class XSearchMapper(ToolMapper):
    """Map XSearch to XAI Responses x_search wire format."""

    tool_type = XSearch

    def map_tool(self, tool: Tool) -> dict[str, Any]:
        return {"type": "x_search"}


class CodeExecutionMapper(ToolMapper):
    """Map CodeExecution to XAI Responses code_interpreter wire format."""

    tool_type = CodeExecution

    def map_tool(self, tool: Tool) -> dict[str, Any]:
        return {"type": "code_interpreter"}


TOOL_MAPPERS: list[ToolMapper] = [
    WebSearchMapper(),
    XSearchMapper(),
    CodeExecutionMapper(),
]

__all__ = ["TOOL_MAPPERS", "CodeExecutionMapper", "XSearchMapper"]
