"""Cohere parameter mappers for text."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.providers.cohere.chat.parameters import (
    MaxTokensMapper as _MaxTokensMapper,
)
from celeste.providers.cohere.chat.parameters import (
    ResponseFormatMapper as _ResponseFormatMapper,
)
from celeste.providers.cohere.chat.parameters import (
    TemperatureMapper as _TemperatureMapper,
)
from celeste.providers.cohere.chat.parameters import (
    ThinkingMapper as _ThinkingMapper,
)

from ...parameters import TextParameter


class TemperatureMapper(_TemperatureMapper):
    """Map temperature to Cohere's temperature parameter."""

    name = TextParameter.TEMPERATURE


class MaxTokensMapper(_MaxTokensMapper):
    """Map max_tokens to Cohere's max_tokens parameter."""

    name = TextParameter.MAX_TOKENS


class ThinkingBudgetMapper(_ThinkingMapper):
    """Translate unified thinking_budget values to Cohere-native format."""

    name = TextParameter.THINKING_BUDGET

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


class OutputSchemaMapper(_ResponseFormatMapper):
    """Map output_schema to Cohere's response_format parameter."""

    name = TextParameter.OUTPUT_SCHEMA


COHERE_PARAMETER_MAPPERS: list[ParameterMapper] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    ThinkingBudgetMapper(),
    OutputSchemaMapper(),
]

__all__ = ["COHERE_PARAMETER_MAPPERS"]
