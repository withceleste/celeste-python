"""HuggingFace parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.providers.huggingface.chat.parameters import (
    ResponseFormatMapper as _ResponseFormatMapper,
)
from celeste.types import TextContent

from ...parameters import TextParameter
from ...protocols.chatcompletions.parameters import (
    MaxTokensMapper,
    TemperatureMapper,
    ToolChoiceMapper,
    ToolsMapper,
)


class OutputSchemaMapper(_ResponseFormatMapper):
    """Map output_schema to HuggingFace's response_format parameter."""

    name = TextParameter.OUTPUT_SCHEMA


HUGGINGFACE_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    OutputSchemaMapper(),
    ToolsMapper(),
    ToolChoiceMapper(),
]

__all__ = ["HUGGINGFACE_PARAMETER_MAPPERS"]
