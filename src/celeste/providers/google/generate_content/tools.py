"""Google GenerateContent API tool mappers."""

import warnings
from typing import Any, ClassVar

from celeste.exceptions import UnsupportedParameterWarning
from celeste.tools import CodeExecution, Tool, ToolMapper, WebSearch


class WebSearchMapper(ToolMapper):
    """Map WebSearch to Google google_search wire format."""

    tool_type = WebSearch
    _supported_fields: ClassVar[set[str]] = {"blocked_domains"}

    def map_tool(self, tool: Tool) -> dict[str, Any]:
        assert isinstance(tool, WebSearch)
        config: dict[str, Any] = {}
        if tool.blocked_domains is not None:
            config["exclude_domains"] = tool.blocked_domains
        for field in type(tool).model_fields:
            if field not in self._supported_fields and getattr(tool, field) is not None:
                warnings.warn(
                    f"WebSearch.{field} is not supported by Google "
                    f"and will be ignored. Workaround: use a raw dict tool instead.",
                    UnsupportedParameterWarning,
                    stacklevel=2,
                )
        return {"google_search": config}


class CodeExecutionMapper(ToolMapper):
    """Map CodeExecution to Google code_execution wire format."""

    tool_type = CodeExecution

    def map_tool(self, tool: Tool) -> dict[str, Any]:
        return {"code_execution": {}}


TOOL_MAPPERS: list[ToolMapper] = [WebSearchMapper(), CodeExecutionMapper()]

__all__ = ["TOOL_MAPPERS", "CodeExecutionMapper", "WebSearchMapper"]
