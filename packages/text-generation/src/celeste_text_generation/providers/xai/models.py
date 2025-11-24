"""XAI models for text generation."""

from celeste import Model, Provider
from celeste.constraints import Choice, Range, Schema
from celeste.core import Parameter
from celeste_text_generation.parameters import TextGenerationParameter

MODELS: list[Model] = [
    Model(
        id="grok-4-1-fast-reasoning",
        provider=Provider.XAI,
        display_name="Grok 4.1 Fast Reasoning",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=30000),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="grok-4-1-fast-non-reasoning",
        provider=Provider.XAI,
        display_name="Grok 4.1 Fast Non-Reasoning",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=30000),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="grok-4-fast-reasoning",
        provider=Provider.XAI,
        display_name="Grok 4 Fast Reasoning",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=30000),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="grok-4-fast-non-reasoning",
        provider=Provider.XAI,
        display_name="Grok 4 Fast Non-Reasoning",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=30000),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="grok-4-0709",
        provider=Provider.XAI,
        display_name="Grok 4",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=64000),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="grok-3-mini",
        provider=Provider.XAI,
        display_name="Grok 3 Mini",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=16000),
            TextGenerationParameter.THINKING_LEVEL: Choice(options=["low", "high"]),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
]
