"""OpenResponses parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.providers.openresponses.responses.parameters import (
    MaxOutputTokensMapper as _MaxOutputTokensMapper,
)
from celeste.providers.openresponses.responses.parameters import (
    TemperatureMapper as _TemperatureMapper,
)
from celeste.providers.openresponses.responses.parameters import (
    TextFormatMapper as _TextFormatMapper,
)

from ...parameters import TextParameter


class TemperatureMapper(_TemperatureMapper):
    """Map temperature to Responses temperature parameter."""

    name = TextParameter.TEMPERATURE


class MaxTokensMapper(_MaxOutputTokensMapper):
    """Map max_tokens to Responses max_output_tokens parameter."""

    name = TextParameter.MAX_TOKENS


class OutputSchemaMapper(_TextFormatMapper):
    """Map output_schema to Responses text.format parameter."""

    name = TextParameter.OUTPUT_SCHEMA


OPENRESPONSES_PARAMETER_MAPPERS: list[ParameterMapper] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    OutputSchemaMapper(),
]

__all__ = ["OPENRESPONSES_PARAMETER_MAPPERS"]
