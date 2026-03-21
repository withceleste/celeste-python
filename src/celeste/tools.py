"""Tool calling types for Celeste."""

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

from celeste.types import Message, Role, ToolCall


class Tool(BaseModel):
    """Base for configurable tools. Subclass per tool type.

    Provider-specific ToolMappers translate these to wire format.
    """

    model_config = ConfigDict(frozen=True)


class WebSearch(Tool):
    """Web search tool with unified cross-provider configuration.

    Config mapping per provider:
    - allowed_domains → Anthropic: allowed_domains, OpenAI: filters.allowed_domains
    - blocked_domains → Anthropic: blocked_domains, Google: exclude_domains
    - max_uses → Anthropic: max_uses
    """

    allowed_domains: list[str] | None = None
    blocked_domains: list[str] | None = None
    max_uses: int | None = None


class XSearch(Tool):
    """X/Twitter search tool (OpenAI/xAI only)."""


class CodeExecution(Tool):
    """Code execution/interpreter tool."""


class ToolMapper(ABC):
    """Maps a single Tool type to provider wire format.

    Parallel to FieldMapper for parameters. One per tool type per provider.
    """

    tool_type: ClassVar[type[Tool]]

    @abstractmethod
    def map_tool(self, tool: Tool) -> dict[str, Any]: ...


type ToolDefinition = Tool | dict[str, Any]


class ToolResult(Message):
    """A tool result for multi-turn tool use."""

    role: Role = Role.USER
    tool_call_id: str
    name: str | None = None


__all__ = [
    "CodeExecution",
    "Tool",
    "ToolCall",
    "ToolDefinition",
    "ToolMapper",
    "ToolResult",
    "WebSearch",
    "XSearch",
]
