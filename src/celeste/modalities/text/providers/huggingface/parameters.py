"""HuggingFace parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.protocols.chatcompletions.parameters import (
    MaxTokensMapper as _MaxTokensMapper,
)
from celeste.protocols.chatcompletions.parameters import (
    TemperatureMapper as _TemperatureMapper,
)
from celeste.providers.huggingface.chat.parameters import (
    ResponseFormatMapper as _ResponseFormatMapper,
)
from celeste.types import TextContent

from ...parameters import TextParameter


class TemperatureMapper(_TemperatureMapper):
    """Map temperature to HuggingFace's temperature parameter."""

    name = TextParameter.TEMPERATURE


class MaxTokensMapper(_MaxTokensMapper):
    """Map max_tokens to HuggingFace's max_tokens parameter."""

    name = TextParameter.MAX_TOKENS


class OutputSchemaMapper(_ResponseFormatMapper):
    """Map output_schema to HuggingFace's response_format parameter."""

    name = TextParameter.OUTPUT_SCHEMA


HUGGINGFACE_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    OutputSchemaMapper(),
]

__all__ = ["HUGGINGFACE_PARAMETER_MAPPERS"]
