"""Chat Completions parameter mappers for text."""

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
from celeste.protocols.chatcompletions.parameters import (
    ToolsMapper as _ToolsMapper,
)
from celeste.types import TextContent

from ...parameters import TextParameter


class TemperatureMapper(_TemperatureMapper):
    """Map temperature to Chat Completions temperature parameter."""

    name = TextParameter.TEMPERATURE


class MaxTokensMapper(_MaxTokensMapper):
    """Map max_tokens to Chat Completions max_tokens parameter."""

    name = TextParameter.MAX_TOKENS


class OutputSchemaMapper(_ResponseFormatMapper):
    """Map output_schema to Chat Completions response_format parameter."""

    name = TextParameter.OUTPUT_SCHEMA


class ToolsMapper(_ToolsMapper):
    """Map tools to Chat Completions tools parameter."""

    name = TextParameter.TOOLS


CHATCOMPLETIONS_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    OutputSchemaMapper(),
    ToolsMapper(),
]

__all__ = ["CHATCOMPLETIONS_PARAMETER_MAPPERS"]
