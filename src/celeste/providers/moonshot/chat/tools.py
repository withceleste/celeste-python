"""Moonshot Chat Completions tool mappers."""

import warnings
from typing import Any, ClassVar

from celeste.exceptions import UnsupportedParameterWarning
from celeste.tools import Tool, ToolMapper, WebSearch


class WebSearchMapper(ToolMapper):
    """Map WebSearch to Moonshot builtin_function wire format."""

    tool_type = WebSearch
    _supported_fields: ClassVar[set[str]] = set()

    def map_tool(self, tool: Tool) -> dict[str, Any]:
        assert isinstance(tool, WebSearch)
        for field in type(tool).model_fields:
            if field not in self._supported_fields and getattr(tool, field) is not None:
                warnings.warn(
                    f"WebSearch.{field} is not supported by Moonshot "
                    f"and will be ignored. Workaround: use a raw dict tool instead.",
                    UnsupportedParameterWarning,
                    stacklevel=2,
                )
        return {"type": "builtin_function", "function": {"name": "$web_search"}}


TOOL_MAPPERS: list[ToolMapper] = [WebSearchMapper()]

__all__ = ["TOOL_MAPPERS", "WebSearchMapper"]
