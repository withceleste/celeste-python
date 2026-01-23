"""Parameters for text modality.

Unified parameters for all text operations (generate, analyze).
Model `parameter_constraints` validates parameter values when defined; unconstrained parameters pass through.
"""

from enum import StrEnum

from pydantic import BaseModel

from celeste.parameters import Parameters


class TextParameter(StrEnum):
    """Unified parameter names for text modality."""

    # Common parameters
    TEMPERATURE = "temperature"
    MAX_TOKENS = "max_tokens"
    SEED = "seed"

    # Text-specific parameters
    THINKING_BUDGET = "thinking_budget"
    THINKING_LEVEL = "thinking_level"
    OUTPUT_SCHEMA = "output_schema"
    WEB_SEARCH = "web_search"
    VERBOSITY = "verbosity"
    X_SEARCH = "x_search"
    CODE_EXECUTION = "code_execution"

    # Media input declarations (for optional_input_types)
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class TextParameters(Parameters):
    """Parameters for text operations."""

    # Common parameters
    temperature: float
    max_tokens: int
    seed: int

    # Text-specific parameters
    thinking_budget: int | str
    thinking_level: str
    output_schema: type[BaseModel]
    web_search: bool
    verbosity: str
    x_search: bool
    code_execution: bool


__all__ = [
    "TextParameter",
    "TextParameters",
]
