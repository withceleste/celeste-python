"""Parameters for text modality.

Unified parameters for all text operations (generate, analyze).
Model `parameter_constraints` validates parameter values when defined; unconstrained parameters pass through.
"""

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field

from celeste.parameters import Parameters
from celeste.tools import ToolChoiceOption, ToolDefinition


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
    TOOLS = "tools"
    TOOL_CHOICE = "tool_choice"
    VERBOSITY = "verbosity"

    # Deprecated: use tools=[WebSearch()], tools=[XSearch()], tools=[CodeExecution()] instead.
    # TODO(deprecation): Remove on 2026-06-07.
    WEB_SEARCH = "web_search"
    X_SEARCH = "x_search"
    CODE_EXECUTION = "code_execution"

    # Media input declarations (for optional_input_types)
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"


class TextParameters(Parameters, total=False):
    """Parameters for text operations."""

    # Common parameters
    temperature: Annotated[
        float, Field(description="Sampling randomness; 0.0 is deterministic.")
    ]
    max_tokens: Annotated[int, Field(description="Maximum tokens to generate.")]
    seed: Annotated[int, Field(description="Seed for deterministic output.")]

    # Text-specific parameters
    thinking_budget: Annotated[
        int | str,
        Field(
            description="Reasoning budget — integer token count, or a preset tier for models that accept one."
        ),
    ]
    thinking_level: Annotated[str, Field(description="Model reasoning depth.")]
    output_schema: Annotated[
        type[BaseModel],
        Field(description="Pydantic model constraining the output shape."),
    ]
    tools: Annotated[
        list[ToolDefinition],
        Field(description="Tools the model may call during generation."),
    ]
    tool_choice: Annotated[
        ToolChoiceOption,
        Field(description="Controls whether and which tool the model must call."),
    ]
    verbosity: Annotated[str, Field(description="Output verbosity level.")]

    # Deprecated: use tools=[WebSearch()], tools=[XSearch()], tools=[CodeExecution()] instead.
    # TODO(deprecation): Remove on 2026-06-07.
    web_search: Annotated[
        bool, Field(description="Deprecated. Use tools=[WebSearch()].")
    ]
    x_search: Annotated[bool, Field(description="Deprecated. Use tools=[XSearch()].")]
    code_execution: Annotated[
        bool, Field(description="Deprecated. Use tools=[CodeExecution()].")
    ]


__all__ = [
    "TextParameter",
    "TextParameters",
]
