"""Parameters for text generation."""

from enum import StrEnum

from pydantic import BaseModel

from celeste.parameters import Parameters


class TextGenerationParameter(StrEnum):
    """Unified parameter names for text generation capability."""

    THINKING_BUDGET = "thinking_budget"
    OUTPUT_SCHEMA = "output_schema"


class TextGenerationParameters(Parameters):
    """Parameters for text generation."""

    temperature: float | None
    max_tokens: int | None
    thinking_budget: int | None
    output_schema: type[BaseModel] | None
