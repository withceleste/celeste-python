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
        for field in type(tool).model_fields:
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


def parse_search_results(response_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract Groq Compound native search result rows."""
    choices = response_data.get("choices", [])
    if not choices:
        return []

    message = choices[0].get("message", {})
    executed_tools = message.get("executed_tools")
    if not isinstance(executed_tools, list):
        return []

    results: list[dict[str, Any]] = []
    for tool in executed_tools:
        if not isinstance(tool, dict):
            continue
        search_results = tool.get("search_results")
        if not isinstance(search_results, dict):
            continue
        rows = search_results.get("results")
        if not isinstance(rows, list):
            continue
        results.extend(row for row in rows if isinstance(row, dict))
    return results


__all__ = [
    "TOOL_MAPPERS",
    "CodeExecutionMapper",
    "WebSearchMapper",
    "parse_search_results",
]
