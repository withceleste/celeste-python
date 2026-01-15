"""xAI parameter mappers for text."""

from celeste.parameters import ParameterMapper
from celeste.providers.xai.responses.parameters import (
    CodeExecutionMapper as _CodeExecutionMapper,
)
from celeste.providers.xai.responses.parameters import (
    MaxOutputTokensMapper as _MaxOutputTokensMapper,
)
from celeste.providers.xai.responses.parameters import (
    ReasoningEffortMapper as _ReasoningEffortMapper,
)
from celeste.providers.xai.responses.parameters import (
    TemperatureMapper as _TemperatureMapper,
)
from celeste.providers.xai.responses.parameters import (
    TextFormatMapper as _TextFormatMapper,
)
from celeste.providers.xai.responses.parameters import (
    WebSearchMapper as _WebSearchMapper,
)
from celeste.providers.xai.responses.parameters import (
    XSearchMapper as _XSearchMapper,
)

from ...parameters import TextParameter


class TemperatureMapper(_TemperatureMapper):
    """Map temperature to xAI's temperature parameter."""

    name = TextParameter.TEMPERATURE


class MaxTokensMapper(_MaxOutputTokensMapper):
    """Map max_tokens to xAI's max_output_tokens parameter."""

    name = TextParameter.MAX_TOKENS


class ThinkingBudgetMapper(_ReasoningEffortMapper):
    """Map thinking_budget to xAI's reasoning.effort parameter."""

    name = TextParameter.THINKING_BUDGET


class OutputSchemaMapper(_TextFormatMapper):
    """Map output_schema to xAI's text.format parameter."""

    name = TextParameter.OUTPUT_SCHEMA


class WebSearchMapper(_WebSearchMapper):
    """Map web_search to xAI's tools parameter."""

    name = TextParameter.WEB_SEARCH


class XSearchMapper(_XSearchMapper):
    """Map x_search to xAI's tools parameter."""

    name = TextParameter.X_SEARCH


class CodeExecutionMapper(_CodeExecutionMapper):
    """Map code_execution to xAI's tools parameter."""

    name = TextParameter.CODE_EXECUTION


XAI_PARAMETER_MAPPERS: list[ParameterMapper] = [
    TemperatureMapper(),
    MaxTokensMapper(),
    ThinkingBudgetMapper(),
    OutputSchemaMapper(),
    WebSearchMapper(),
    XSearchMapper(),
    CodeExecutionMapper(),
]

__all__ = ["XAI_PARAMETER_MAPPERS"]
