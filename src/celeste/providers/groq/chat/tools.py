"""Groq Chat Completions tool mappers."""

import warnings
from typing import Any, ClassVar

from celeste.exceptions import UnsupportedParameterWarning
from celeste.tools import CodeExecution, Tool, ToolMapper, WebSearch


class WebSearchMapper(ToolMapper):
    """Map WebSearch to Groq browser_search wire format."""

    tool_type = WebSearch
    _supported_fields: ClassVar[set[str]] = set()

    def map_tool(self, tool: Tool) -> dict[str, Any]:
        assert isinstance(tool, WebSearch)
        for field in tool.model_fields:
            if field not in self._supported_fields and getattr(tool, field) is not None:
                warnings.warn(
                    f"WebSearch.{field} is not supported by Groq "
                    f"and will be ignored. Workaround: use a raw dict tool instead.",
                    UnsupportedParameterWarning,
                    stacklevel=2,
                )
        return {"type": "browser_search"}


class CodeExecutionMapper(ToolMapper):
    """Map CodeExecution to Groq code_interpreter wire format."""

    tool_type = CodeExecution

    def map_tool(self, tool: Tool) -> dict[str, Any]:
        return {"type": "code_interpreter"}


TOOL_MAPPERS: list[ToolMapper] = [WebSearchMapper(), CodeExecutionMapper()]

__all__ = ["TOOL_MAPPERS", "CodeExecutionMapper", "WebSearchMapper"]
