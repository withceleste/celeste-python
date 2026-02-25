"""Mistral parameter mappers for text."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.protocols.chatcompletions.parameters import (
    MaxTokensMapper as _MaxTokensMapper,
)
from celeste.protocols.chatcompletions.parameters import (
    TemperatureMapper as _TemperatureMapper,
)
from celeste.providers.mistral.chat.parameters import (
    ResponseFormatMapper as _ResponseFormatMapper,
)
from celeste.types import TextContent

from ...parameters import TextParameter


class TemperatureMapper(_TemperatureMapper):
    """Map temperature to Mistral's temperature parameter."""

    name = TextParameter.TEMPERATURE


class MaxTokensMapper(_MaxTokensMapper):
    """Map max_tokens to Mistral's max_tokens parameter."""

    name = TextParameter.MAX_TOKENS


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

        # Map unified values to Mistral's prompt_mode
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


MISTRAL_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    ThinkingBudgetMapper(),
    OutputSchemaMapper(),
]

__all__ = ["MISTRAL_PARAMETER_MAPPERS"]
