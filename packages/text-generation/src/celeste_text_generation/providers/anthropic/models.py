"""Anthropic models for text generation."""

from celeste import Model, Provider
from celeste.constraints import Range, Schema
from celeste_text_generation.parameters import TextGenerationParameter

MODELS: list[Model] = [
    Model(
        id="claude-sonnet-4-5",
        provider=Provider.ANTHROPIC,
        display_name="Claude Sonnet 4.5",
        streaming=True,
        parameter_constraints={
            TextGenerationParameter.THINKING_BUDGET: Range(min=-1, max=64000),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="claude-haiku-4-5",
        provider=Provider.ANTHROPIC,
        display_name="Claude Haiku 4.5",
        streaming=True,
        parameter_constraints={
            TextGenerationParameter.THINKING_BUDGET: Range(min=-1, max=32000),
        },
    ),
    Model(
        id="claude-opus-4-1",
        provider=Provider.ANTHROPIC,
        display_name="Claude Opus 4.1",
        streaming=True,
        parameter_constraints={
            TextGenerationParameter.THINKING_BUDGET: Range(min=-1, max=32000),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="claude-sonnet-4-20250514",
        provider=Provider.ANTHROPIC,
        display_name="Claude Sonnet 4",
        streaming=True,
        parameter_constraints={
            TextGenerationParameter.THINKING_BUDGET: Range(min=-1, max=64000),
        },
    ),
    Model(
        id="claude-opus-4-20250514",
        provider=Provider.ANTHROPIC,
        display_name="Claude Opus 4",
        streaming=True,
        parameter_constraints={
            TextGenerationParameter.THINKING_BUDGET: Range(min=-1, max=32000),
        },
    ),
]
