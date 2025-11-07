"""Google models."""

from celeste import Model, Provider
from celeste.constraints import Range, Schema
from celeste.core import Parameter
from celeste_text_generation.parameters import TextGenerationParameter

MODELS: list[Model] = [
    Model(
        id="gemini-2.5-flash",
        provider=Provider.GOOGLE,
        display_name="Gemini 2.5 Flash",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=8192),
            # Flash: allows -1 (dynamic), 0 (disable), or >= 0
            TextGenerationParameter.THINKING_BUDGET: Range(min=-1, max=24576),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="gemini-2.5-flash-lite",
        provider=Provider.GOOGLE,
        display_name="Gemini 2.5 Flash Lite",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=8192),
            # Flash Lite: allows -1 (dynamic), 0 (disable), or >= 512
            TextGenerationParameter.THINKING_BUDGET: Range(
                min=512, max=24576, special_values=[-1, 0]
            ),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="gemini-2.5-pro",
        provider=Provider.GOOGLE,
        display_name="Gemini 2.5 Pro",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=8192),
            # Pro: allows -1 (dynamic) or >= 128 (cannot use 0)
            TextGenerationParameter.THINKING_BUDGET: Range(
                min=128, max=32768, special_values=[-1]
            ),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
]
