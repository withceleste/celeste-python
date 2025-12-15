"""Mistral Chat parameter mappers for text generation."""

from typing import Any

from celeste_mistral.chat.parameters import (
    MaxTokensMapper as _MaxTokensMapper,
)
from celeste_mistral.chat.parameters import (
    OutputSchemaMapper as _OutputSchemaMapper,
)
from celeste_mistral.chat.parameters import (
    TemperatureMapper as _TemperatureMapper,
)

from celeste.core import Parameter
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste_text_generation.parameters import TextGenerationParameter


class TemperatureMapper(_TemperatureMapper):
    name = Parameter.TEMPERATURE


class MaxTokensMapper(_MaxTokensMapper):
    name = Parameter.MAX_TOKENS


class ThinkingBudgetMapper(ParameterMapper):
    """Map thinking_budget to Mistral prompt_mode (Pattern 3: Coercion).

    Mistral uses prompt_mode instead of a thinking parameter, so this creates
    a unified parameter that maps to the provider-specific format.
    """

    name = TextGenerationParameter.THINKING_BUDGET

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


class OutputSchemaMapper(_OutputSchemaMapper):
    name = TextGenerationParameter.OUTPUT_SCHEMA


MISTRAL_PARAMETER_MAPPERS: list[ParameterMapper] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    ThinkingBudgetMapper(),
    OutputSchemaMapper(),
]

__all__ = ["MISTRAL_PARAMETER_MAPPERS"]
