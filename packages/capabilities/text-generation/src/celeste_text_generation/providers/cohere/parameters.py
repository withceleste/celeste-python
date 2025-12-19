"""Cohere Chat parameter mappers for text generation."""

from typing import Any

from celeste_cohere.chat.parameters import (
    MaxTokensMapper as _MaxTokensMapper,
)
from celeste_cohere.chat.parameters import (
    OutputSchemaMapper as _OutputSchemaMapper,
)
from celeste_cohere.chat.parameters import (
    TemperatureMapper as _TemperatureMapper,
)
from celeste_cohere.chat.parameters import (
    ThinkingMapper as _ThinkingMapper,
)

from celeste.core import Parameter
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste_text_generation.parameters import TextGenerationParameter


class TemperatureMapper(_TemperatureMapper):
    name = Parameter.TEMPERATURE


class MaxTokensMapper(_MaxTokensMapper):
    name = Parameter.MAX_TOKENS


class ThinkingBudgetMapper(_ThinkingMapper):
    """Translate unified thinking_budget values to Cohere-native format."""

    name = TextGenerationParameter.THINKING_BUDGET

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform thinking_budget with unified value translation."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Translate unified → provider-native
        if validated_value == -1:
            provider_value = "enabled"
        elif validated_value == 0:
            provider_value = "disabled"
        else:
            provider_value = validated_value

        return super().map(request, provider_value, model)


class OutputSchemaMapper(_OutputSchemaMapper):
    name = TextGenerationParameter.OUTPUT_SCHEMA


COHERE_PARAMETER_MAPPERS: list[ParameterMapper] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    ThinkingBudgetMapper(),
    OutputSchemaMapper(),
]

__all__ = ["COHERE_PARAMETER_MAPPERS"]
