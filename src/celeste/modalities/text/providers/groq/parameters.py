"""Groq parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.providers.groq.chat.parameters import (
    MaxTokensMapper as _MaxTokensMapper,
)
from celeste.providers.groq.chat.parameters import (
    ResponseFormatMapper as _ResponseFormatMapper,
)
from celeste.providers.groq.chat.parameters import (
    TemperatureMapper as _TemperatureMapper,
)

from ...parameters import TextParameter


class TemperatureMapper(_TemperatureMapper):
    """Map temperature to Groq's temperature parameter."""

    name = TextParameter.TEMPERATURE


class MaxTokensMapper(_MaxTokensMapper):
    """Map max_tokens to Groq's max_tokens parameter."""

    name = TextParameter.MAX_TOKENS


class OutputSchemaMapper(_ResponseFormatMapper):
    """Map output_schema to Groq's response_format parameter."""

    name = TextParameter.OUTPUT_SCHEMA


GROQ_PARAMETER_MAPPERS: list[ParameterMapper] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    OutputSchemaMapper(),
]

__all__ = ["GROQ_PARAMETER_MAPPERS"]
