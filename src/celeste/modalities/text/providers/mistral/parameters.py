"""Mistral parameter mappers for text."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.providers.mistral.chat.parameters import (
    ResponseFormatMapper as _ResponseFormatMapper,
)
from celeste.types import TextContent

from ...parameters import TextParameter
from ...protocols.chatcompletions.parameters import (
    MaxTokensMapper,
    TemperatureMapper,
    ToolsMapper,
)
from ...protocols.chatcompletions.parameters import (
    ToolChoiceMapper as _ToolChoiceMapper,
)


class ThinkingBudgetMapper(ParameterMapper[TextContent]):
    """Map thinking_budget to Mistral's prompt_mode parameter."""

    name = TextParameter.THINKING_BUDGET

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform thinking_budget into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        if validated_value == -1:
            request["prompt_mode"] = "reasoning"
        elif validated_value == 0:
            request["prompt_mode"] = None
        else:
            request["prompt_mode"] = "reasoning"

        return request


class OutputSchemaMapper(_ResponseFormatMapper):
    """Map output_schema to Mistral's response_format parameter."""

    name = TextParameter.OUTPUT_SCHEMA


class ToolChoiceMapper(_ToolChoiceMapper):
    """Map tool_choice to Mistral's tool_choice parameter.

    Mistral uses "any" instead of "required".
    """

    name = TextParameter.TOOL_CHOICE

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform tool_choice, translating 'required' to 'any'."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        if validated_value == "required":
            request["tool_choice"] = "any"
            return request
        return super().map(request, validated_value, model)


MISTRAL_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    ThinkingBudgetMapper(),
    OutputSchemaMapper(),
    ToolsMapper(),
    ToolChoiceMapper(),
]

__all__ = ["MISTRAL_PARAMETER_MAPPERS"]
