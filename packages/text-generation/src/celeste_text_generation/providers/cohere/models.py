"""Cohere models for text generation."""

from celeste import Model, Provider
from celeste.constraints import Range, Schema
from celeste.core import Parameter
from celeste_text_generation.parameters import TextGenerationParameter

MODELS: list[Model] = [
    Model(
        id="command-a-03-2025",
        provider=Provider.COHERE,
        display_name="Command A 03-2025",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=1.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=4096, step=1),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
            # thinking_budget: Not confirmed for this model, omit constraint
        },
    ),
    Model(
        id="command-r-plus",
        provider=Provider.COHERE,
        display_name="Command R+",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=1.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=4096, step=1),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
            # command-r-plus supports reasoning (optimized for complex reasoning)
            TextGenerationParameter.THINKING_BUDGET: Range(min=-1, max=31000, step=1),
        },
    ),
    Model(
        id="command-r",
        provider=Provider.COHERE,
        display_name="Command R",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=1.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=4096, step=1),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
            # thinking_budget: Support unclear, omit constraint for now
        },
    ),
    Model(
        id="command-r7b-12-2024",
        provider=Provider.COHERE,
        display_name="Command R7B",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=1.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=4096, step=1),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
            # thinking_budget: Support unclear, omit constraint for now
        },
    ),
]
