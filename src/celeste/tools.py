"""Tool calling types for Celeste."""

from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any, ClassVar, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic import ValidationError as PydanticValidationError

from celeste.exceptions import ValidationError
from celeste.types import Role, ToolCall, ToolResultContent


class Tool(BaseModel):
    """Base for configurable tools. Subclass per tool type.

    Provider-specific ToolMappers translate these to wire format.
    The `kind` discriminator lets serialized tools rehydrate across
    JSON boundaries (e.g. consumers that relay parameters as JSON).
    """

    model_config = ConfigDict(frozen=True)


class WebSearch(Tool):
    """Web search tool with unified cross-provider configuration.

    Config mapping per provider:
    - allowed_domains → Anthropic: allowed_domains, OpenAI: filters.allowed_domains
    - blocked_domains → Anthropic: blocked_domains, Google: exclude_domains
    - max_uses → Anthropic: max_uses
    """

    kind: Literal["web_search"] = "web_search"
    allowed_domains: list[str] | None = None
    blocked_domains: list[str] | None = None
    max_uses: int | None = None


class XSearch(Tool):
    """X/Twitter search tool (OpenAI/xAI only)."""

    kind: Literal["x_search"] = "x_search"


class CodeExecution(Tool):
    """Code execution/interpreter tool."""

    kind: Literal["code_execution"] = "code_execution"


class ToolMapper(ABC):
    """Maps a single Tool type to provider wire format.

    Parallel to FieldMapper for parameters. One per tool type per provider.
    """

    tool_type: ClassVar[type[Tool]]

    @abstractmethod
    def map_tool(self, tool: Tool) -> dict[str, Any]: ...


type ToolDefinition = Tool | dict[str, Any]

_TOOL_KINDS: dict[str, type[Tool]] = {
    "web_search": WebSearch,
    "x_search": XSearch,
    "code_execution": CodeExecution,
}


def rehydrate_tools(tools: list[ToolDefinition]) -> list[ToolDefinition]:
    """Rebuild Tool instances from kind-tagged dicts (JSON round-trips)."""
    return [
        _TOOL_KINDS[item["kind"]].model_validate(item)
        if isinstance(item, dict) and item.get("kind") in _TOOL_KINDS
        else item
        for item in tools
    ]


def _tool_parameter_models(tools: object | None) -> dict[str, type[BaseModel]]:
    if not isinstance(tools, list):
        return {}

    models: dict[str, type[BaseModel]] = {}
    for tool in tools:
        if not isinstance(tool, dict):
            continue
        name = tool.get("name")
        parameters = tool.get("parameters")
        if (
            isinstance(name, str)
            and isinstance(parameters, type)
            and issubclass(parameters, BaseModel)
        ):
            models[name] = parameters
    return models


def validate_tool_calls(
    tool_calls: list[ToolCall],
    tools: object | None,
) -> list[ToolCall]:
    """Validate returned tool calls against local Pydantic tool parameter models."""
    parameter_models = _tool_parameter_models(tools)
    if not parameter_models:
        return tool_calls

    validated_calls: list[ToolCall] = []
    for tool_call in tool_calls:
        parameters_model = parameter_models.get(tool_call.name)
        if parameters_model is None:
            validated_calls.append(tool_call)
            continue

        try:
            validated_arguments = parameters_model.model_validate(tool_call.arguments)
        except PydanticValidationError as exc:
            raise ValidationError(
                f"Tool call '{tool_call.name}' arguments failed validation: {exc}"
            ) from exc

        validated_calls.append(
            tool_call.model_copy(
                update={
                    "arguments": validated_arguments.model_dump(
                        mode="json",
                        exclude_unset=True,
                    )
                }
            )
        )
    return validated_calls


class ToolChoice(StrEnum):
    """Controls whether the model must use tools."""

    AUTO = "auto"
    REQUIRED = "required"
    NONE = "none"


type ToolChoiceOption = ToolChoice | ToolDefinition


class ToolResult(BaseModel):
    """A tool result for multi-turn tool use."""

    model_config = ConfigDict(extra="allow")

    role: Role = Role.USER
    content: ToolResultContent
    tool_call_id: str
    name: str | None = None


class ToolOutput[Content](BaseModel):
    """Structured output returned by executable tools."""

    content: Content
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolError[Content](BaseModel):
    """Structured error returned by executable tools."""

    content: Content
    code: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "CodeExecution",
    "Tool",
    "ToolCall",
    "ToolChoice",
    "ToolChoiceOption",
    "ToolDefinition",
    "ToolError",
    "ToolMapper",
    "ToolOutput",
    "ToolResult",
    "ToolResultContent",
    "WebSearch",
    "XSearch",
    "rehydrate_tools",
    "validate_tool_calls",
]
