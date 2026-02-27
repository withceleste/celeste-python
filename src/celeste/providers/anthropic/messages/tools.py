"""Anthropic Messages API tool mappers."""

from typing import Any

from celeste.tools import Tool, ToolMapper, WebSearch


class WebSearchMapper(ToolMapper):
    """Map WebSearch to Anthropic web_search_20250305 wire format."""

    tool_type = WebSearch

    def map_tool(self, tool: Tool) -> dict[str, Any]:
        assert isinstance(tool, WebSearch)
        result: dict[str, Any] = {"type": "web_search_20250305", "name": "web_search"}
        if tool.allowed_domains is not None:
            result["allowed_domains"] = tool.allowed_domains
        if tool.blocked_domains is not None:
            result["blocked_domains"] = tool.blocked_domains
        if tool.max_uses is not None:
            result["max_uses"] = tool.max_uses
        return result


TOOL_MAPPERS: list[ToolMapper] = [WebSearchMapper()]

__all__ = ["TOOL_MAPPERS", "WebSearchMapper"]
