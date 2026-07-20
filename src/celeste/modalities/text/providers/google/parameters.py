"""Google parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.providers.google.generate_content.parameters import (
    MaxOutputTokensMapper as _VertexMaxOutputTokensMapper,
)
from celeste.providers.google.generate_content.parameters import (
    ResponseJsonSchemaMapper as _VertexResponseJsonSchemaMapper,
)
from celeste.providers.google.generate_content.parameters import (
    TemperatureMapper as _VertexTemperatureMapper,
)
from celeste.providers.google.generate_content.parameters import (
    ThinkingBudgetMapper as _VertexThinkingBudgetMapper,
)
from celeste.providers.google.generate_content.parameters import (
    ThinkingLevelMapper as _VertexThinkingLevelMapper,
)
from celeste.providers.google.generate_content.parameters import (
    ToolChoiceMapper as _VertexToolChoiceMapper,
)
from celeste.providers.google.generate_content.parameters import (
    ToolsMapper as _VertexToolsMapper,
)
from celeste.providers.google.interactions.parameters import (
    MaxOutputTokensMapper as _InteractionsMaxOutputTokensMapper,
)
from celeste.providers.google.interactions.parameters import (
    ResponseFormatMapper as _InteractionsResponseFormatMapper,
)
from celeste.providers.google.interactions.parameters import (
    TemperatureMapper as _InteractionsTemperatureMapper,
)
from celeste.providers.google.interactions.parameters import (
    ThinkingLevelMapper as _InteractionsThinkingLevelMapper,
)
from celeste.providers.google.interactions.parameters import (
    ToolChoiceMapper as _InteractionsToolChoiceMapper,
)
from celeste.providers.google.interactions.parameters import (
    ToolsMapper as _InteractionsToolsMapper,
)
from celeste.types import TextContent

from ...parameters import TextParameter


class VertexTemperatureMapper(_VertexTemperatureMapper[TextContent]):
    """Map temperature to Google's generationConfig.temperature parameter."""

    name = TextParameter.TEMPERATURE


class VertexMaxTokensMapper(_VertexMaxOutputTokensMapper[TextContent]):
    """Map max_tokens to Google's generationConfig.maxOutputTokens parameter."""

    name = TextParameter.MAX_TOKENS


class VertexThinkingBudgetMapper(_VertexThinkingBudgetMapper[TextContent]):
    """Map thinking_budget to Google's generationConfig.thinkingConfig.thinkingBudget parameter."""

    name = TextParameter.THINKING_BUDGET


class VertexThinkingLevelMapper(_VertexThinkingLevelMapper[TextContent]):
    """Map thinking_level to Google's generationConfig.thinkingConfig.thinkingLevel parameter."""

    name = TextParameter.THINKING_LEVEL


class VertexOutputSchemaMapper(_VertexResponseJsonSchemaMapper):
    """Map output_schema to Google's generationConfig.responseJsonSchema parameter."""

    name = TextParameter.OUTPUT_SCHEMA


class VertexToolsMapper(_VertexToolsMapper[TextContent]):
    """Map tools to Google's tools parameter."""

    name = TextParameter.TOOLS


class VertexToolChoiceMapper(_VertexToolChoiceMapper[TextContent]):
    """Map tool_choice to Google's tool_choice parameter."""

    name = TextParameter.TOOL_CHOICE


GOOGLE_VERTEX_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    VertexTemperatureMapper(),
    VertexMaxTokensMapper(),
    VertexThinkingBudgetMapper(),
    VertexThinkingLevelMapper(),
    VertexOutputSchemaMapper(),
    VertexToolsMapper(),
    VertexToolChoiceMapper(),
]


class InteractionsTemperatureMapper(_InteractionsTemperatureMapper):
    """Map temperature to Google's generation_config.temperature parameter."""

    name = TextParameter.TEMPERATURE


class InteractionsMaxTokensMapper(_InteractionsMaxOutputTokensMapper):
    """Map max_tokens to Google's generation_config.max_output_tokens parameter."""

    name = TextParameter.MAX_TOKENS


class InteractionsThinkingLevelMapper(_InteractionsThinkingLevelMapper[TextContent]):
    """Map thinking_level to Google's generation_config.thinking_level parameter."""

    name = TextParameter.THINKING_LEVEL


class InteractionsOutputSchemaMapper(_InteractionsResponseFormatMapper):
    """Map output_schema to Google's response_format parameter."""

    name = TextParameter.OUTPUT_SCHEMA


class InteractionsToolsMapper(_InteractionsToolsMapper):
    """Map tools to Google's tools parameter."""

    name = TextParameter.TOOLS


class InteractionsToolChoiceMapper(_InteractionsToolChoiceMapper):
    """Map tool_choice to Google's tool_choice parameter."""

    name = TextParameter.TOOL_CHOICE


GOOGLE_INTERACTIONS_PARAMETER_MAPPERS: list[ParameterMapper[TextContent]] = [
    InteractionsTemperatureMapper(),
    InteractionsMaxTokensMapper(),
    InteractionsThinkingLevelMapper(),
    InteractionsOutputSchemaMapper(),
    InteractionsToolsMapper(),
    InteractionsToolChoiceMapper(),
]

__all__ = ["GOOGLE_INTERACTIONS_PARAMETER_MAPPERS", "GOOGLE_VERTEX_PARAMETER_MAPPERS"]
