"""OpenResponses parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.protocols.openresponses.parameters import (
    MaxOutputTokensMapper as _MaxOutputTokensMapper,
)
from celeste.protocols.openresponses.parameters import (
    TemperatureMapper as _TemperatureMapper,
)
from celeste.protocols.openresponses.parameters import (
    TextFormatMapper as _TextFormatMapper,
)
from celeste.protocols.openresponses.parameters import (
    ToolsMapper as _ToolsMapper,
)
from celeste.types import TextContent

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


class ToolsMapper(_ToolsMapper):
    """Map tools to Responses tools parameter."""

    name = TextParameter.TOOLS


OPENRESPONSES_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    OutputSchemaMapper(),
    ToolsMapper(),
]

__all__ = ["OPENRESPONSES_PARAMETER_MAPPERS"]
