"""Groq Chat Completions tool mappers."""

from typing import Any

from celeste.tools import CodeExecution, Tool, ToolMapper, WebSearch


class WebSearchMapper(ToolMapper):
    """Map WebSearch to Groq browser_search wire format."""

    tool_type = WebSearch

    def map_tool(self, tool: Tool) -> dict[str, Any]:
        return {"type": "browser_search"}


class CodeExecutionMapper(ToolMapper):
    """Map CodeExecution to Groq code_interpreter wire format."""

    tool_type = CodeExecution

    def map_tool(self, tool: Tool) -> dict[str, Any]:
        return {"type": "code_interpreter"}


TOOL_MAPPERS: list[ToolMapper] = [WebSearchMapper(), CodeExecutionMapper()]

__all__ = ["TOOL_MAPPERS", "CodeExecutionMapper", "WebSearchMapper"]
