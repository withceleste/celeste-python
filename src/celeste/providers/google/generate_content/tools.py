"""Google GenerateContent API tool mappers."""

from typing import Any

from celeste.tools import CodeExecution, Tool, ToolMapper, WebSearch


class WebSearchMapper(ToolMapper):
    """Map WebSearch to Google google_search wire format."""

    tool_type = WebSearch

    def map_tool(self, tool: Tool) -> dict[str, Any]:
        assert isinstance(tool, WebSearch)
        config: dict[str, Any] = {}
        if tool.blocked_domains is not None:
            config["exclude_domains"] = tool.blocked_domains
        return {"google_search": config}


class CodeExecutionMapper(ToolMapper):
    """Map CodeExecution to Google code_execution wire format."""

    tool_type = CodeExecution

    def map_tool(self, tool: Tool) -> dict[str, Any]:
        return {"code_execution": {}}


TOOL_MAPPERS: list[ToolMapper] = [WebSearchMapper(), CodeExecutionMapper()]

__all__ = ["TOOL_MAPPERS", "CodeExecutionMapper", "WebSearchMapper"]
