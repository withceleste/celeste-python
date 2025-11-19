"""Parameters for text generation."""

from enum import StrEnum

from pydantic import BaseModel

from celeste.parameters import Parameters


class TextGenerationParameter(StrEnum):
    """Unified parameter names for text generation capability."""

    THINKING_BUDGET = "thinking_budget"
    THINKING_LEVEL = "thinking_level"
    OUTPUT_SCHEMA = "output_schema"
    VERBOSITY = "verbosity"


class TextGenerationParameters(Parameters):
    """Parameters for text generation."""

    temperature: float | None
    max_tokens: int | None
    thinking_budget: int | None
    thinking_level: str | None
    verbosity: str | None
    output_schema: type[BaseModel] | None
