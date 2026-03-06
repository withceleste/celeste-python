"""Moonshot Chat Completions tool mappers."""

from typing import Any

from celeste.tools import Tool, ToolMapper, WebSearch


class WebSearchMapper(ToolMapper):
    """Map WebSearch to Moonshot builtin_function wire format."""

    tool_type = WebSearch

    def map_tool(self, tool: Tool) -> dict[str, Any]:
        return {"type": "builtin_function", "function": {"name": "$web_search"}}


TOOL_MAPPERS: list[ToolMapper] = [WebSearchMapper()]

__all__ = ["TOOL_MAPPERS", "WebSearchMapper"]
