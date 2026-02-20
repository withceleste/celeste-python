"""Moonshot parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.protocols.chatcompletions.parameters import (
    MaxTokensMapper as _MaxTokensMapper,
)
from celeste.protocols.chatcompletions.parameters import (
    ResponseFormatMapper as _ResponseFormatMapper,
)
from celeste.protocols.chatcompletions.parameters import (
    TemperatureMapper as _TemperatureMapper,
)

from ...parameters import TextParameter


class TemperatureMapper(_TemperatureMapper):
    """Map temperature to Moonshot's temperature parameter."""

    name = TextParameter.TEMPERATURE


class MaxTokensMapper(_MaxTokensMapper):
    """Map max_tokens to Moonshot's max_tokens parameter."""

    name = TextParameter.MAX_TOKENS


class OutputSchemaMapper(_ResponseFormatMapper):
    """Map output_schema to Moonshot's response_format parameter."""

    name = TextParameter.OUTPUT_SCHEMA


MOONSHOT_PARAMETER_MAPPERS: list[ParameterMapper] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    OutputSchemaMapper(),
]

__all__ = ["MOONSHOT_PARAMETER_MAPPERS"]
