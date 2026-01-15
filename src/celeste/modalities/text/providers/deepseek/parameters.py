"""DeepSeek parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.providers.deepseek.chat.parameters import (
    MaxTokensMapper as _MaxTokensMapper,
)
from celeste.providers.deepseek.chat.parameters import (
    ResponseFormatMapper as _ResponseFormatMapper,
)
from celeste.providers.deepseek.chat.parameters import (
    TemperatureMapper as _TemperatureMapper,
)

from ...parameters import TextParameter


class TemperatureMapper(_TemperatureMapper):
    """Map temperature to DeepSeek's temperature parameter."""

    name = TextParameter.TEMPERATURE


class MaxTokensMapper(_MaxTokensMapper):
    """Map max_tokens to DeepSeek's max_tokens parameter."""

    name = TextParameter.MAX_TOKENS


class OutputSchemaMapper(_ResponseFormatMapper):
    """Map output_schema to DeepSeek's response_format parameter."""

    name = TextParameter.OUTPUT_SCHEMA


DEEPSEEK_PARAMETER_MAPPERS: list[ParameterMapper] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    OutputSchemaMapper(),
]

__all__ = ["DEEPSEEK_PARAMETER_MAPPERS"]
