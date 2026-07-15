"""Moonshot parameter mappers for text."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.protocols.chatcompletions.parameters import (
    ToolsMapper as _ToolsMapper,
)
from celeste.providers.moonshot.chat.tools import TOOL_MAPPERS as MOONSHOT_TOOL_MAPPERS
from celeste.types import TextContent

from ...parameters import TextParameter
from ...protocols.chatcompletions.parameters import (
    MaxTokensMapper as _MaxTokensMapper,
)
from ...protocols.chatcompletions.parameters import (
    OutputSchemaMapper,
)
from ...protocols.chatcompletions.parameters import (
    TemperatureMapper as _TemperatureMapper,
)
from ...protocols.chatcompletions.parameters import (
    ToolChoiceMapper as _ToolChoiceMapper,
)


class ToolsMapper(_ToolsMapper):
    """Map tools to Moonshot's tools parameter."""

    name = TextParameter.TOOLS
    _tool_mappers = MOONSHOT_TOOL_MAPPERS


class ToolChoiceMapper(_ToolChoiceMapper):
    name = TextParameter.TOOL_CHOICE


class TemperatureMapper(_TemperatureMapper):
    """Map temperature when the model catalog supports it."""

    def map(
        self, request: dict[str, Any], value: object, model: Model
    ) -> dict[str, Any]:
        if self._warn_if_unsupported(value, model):
            return request
        return super().map(request, value, model)


class MaxTokensMapper(_MaxTokensMapper):
    """Map max_tokens to Moonshot's current field name."""

    field = "max_completion_tokens"


MOONSHOT_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    OutputSchemaMapper(),
    ToolsMapper(),
    ToolChoiceMapper(),
]

__all__ = ["MOONSHOT_PARAMETER_MAPPERS"]
