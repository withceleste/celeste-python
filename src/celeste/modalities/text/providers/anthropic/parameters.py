"""Anthropic parameter mappers for text."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.providers.anthropic.messages.parameters import (
    MaxTokensMapper as _MaxTokensMapper,
)
from celeste.providers.anthropic.messages.parameters import (
    OutputFormatMapper as _OutputFormatMapper,
)
from celeste.providers.anthropic.messages.parameters import (
    TemperatureMapper as _TemperatureMapper,
)
from celeste.providers.anthropic.messages.parameters import (
    ThinkingMapper as _ThinkingMapper,
)
from celeste.providers.anthropic.messages.parameters import (
    ToolsMapper as _ToolsMapper,
)
from celeste.types import TextContent

from ...parameters import TextParameter


class TemperatureMapper(_TemperatureMapper):
    """Map temperature to Anthropic's temperature parameter."""

    name = TextParameter.TEMPERATURE


class MaxTokensMapper(_MaxTokensMapper):
    """Map max_tokens to Anthropic's max_tokens parameter."""

    name = TextParameter.MAX_TOKENS


class ThinkingBudgetMapper(_ThinkingMapper):
    """Map thinking_budget to Anthropic's thinking parameter."""

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
            provider_value = "auto"
        else:
            provider_value = validated_value

        return super().map(request, provider_value, model)


class OutputSchemaMapper(_OutputFormatMapper):
    """Map output_schema to Anthropic's output_format parameter."""

    name = TextParameter.OUTPUT_SCHEMA


class ToolsMapper(_ToolsMapper):
    """Map tools to Anthropic's tools parameter."""

    name = TextParameter.TOOLS


ANTHROPIC_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    ThinkingBudgetMapper(),
    OutputSchemaMapper(),
    ToolsMapper(),
]

__all__ = ["ANTHROPIC_PARAMETER_MAPPERS"]
