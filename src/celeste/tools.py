"""Tool calling types for Celeste."""

from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic import ValidationError as PydanticValidationError

from celeste.exceptions import ValidationError
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


class ToolResult(Message):
    """A tool result for multi-turn tool use."""

    role: Role = Role.USER
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
    "WebSearch",
    "XSearch",
    "validate_tool_calls",
]
