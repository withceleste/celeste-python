"""Mistral models for text generation."""

from celeste import Model, Provider
from celeste.constraints import Range, Schema
from celeste.core import Parameter
from celeste_text_generation.parameters import TextGenerationParameter

MODELS: list[Model] = [
    Model(
        id="mistral-large-latest",
        provider=Provider.MISTRAL,
        display_name="Mistral Large",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="mistral-medium-latest",
        provider=Provider.MISTRAL,
        display_name="Mistral Medium",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="mistral-small-latest",
        provider=Provider.MISTRAL,
        display_name="Mistral Small",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="mistral-tiny",
        provider=Provider.MISTRAL,
        display_name="Mistral Tiny",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="open-mistral-7b",
        provider=Provider.MISTRAL,
        display_name="Open Mistral 7B",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="open-mixtral-8x7b",
        provider=Provider.MISTRAL,
        display_name="Open Mixtral 8x7B",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="open-mixtral-8x22b",
        provider=Provider.MISTRAL,
        display_name="Open Mixtral 8x22B",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="codestral-latest",
        provider=Provider.MISTRAL,
        display_name="Codestral",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="devstral-medium-latest",
        provider=Provider.MISTRAL,
        display_name="Devstral Medium",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="pixtral-12b-2409",
        provider=Provider.MISTRAL,
        display_name="Pixtral 12B",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="ministral-8b-latest",
        provider=Provider.MISTRAL,
        display_name="Ministral 8B",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="voxtral-mini-2507",
        provider=Provider.MISTRAL,
        display_name="Voxtral Mini",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="magistral-small-latest",
        provider=Provider.MISTRAL,
        display_name="Magistral Small",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
            TextGenerationParameter.THINKING_BUDGET: Range(min=-1, max=32768, step=1),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="magistral-medium-latest",
        provider=Provider.MISTRAL,
        display_name="Magistral Medium",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
            TextGenerationParameter.THINKING_BUDGET: Range(min=-1, max=32768, step=1),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
]
