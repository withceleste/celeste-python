"""OpenAI models for text generation."""

from celeste import Model, Provider
from celeste.constraints import Choice, Range, Schema
from celeste.core import Parameter
from celeste_text_generation.parameters import TextGenerationParameter

MODELS: list[Model] = [
    Model(
        id="gpt-4o",
        provider=Provider.OPENAI,
        display_name="GPT-4o",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=16384),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="gpt-4o-mini",
        provider=Provider.OPENAI,
        display_name="GPT-4o Mini",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=16384),
        },
    ),
    Model(
        id="gpt-4-turbo",
        provider=Provider.OPENAI,
        display_name="GPT-4 Turbo",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=4096),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="gpt-4",
        provider=Provider.OPENAI,
        display_name="GPT-4",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=8192),
        },
    ),
    Model(
        id="gpt-3.5-turbo",
        provider=Provider.OPENAI,
        display_name="GPT-3.5 Turbo",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=4096),
        },
    ),
    Model(
        id="gpt-5",
        provider=Provider.OPENAI,
        display_name="GPT-5",
        streaming=True,
        parameter_constraints={
            Parameter.MAX_TOKENS: Range(min=1, max=128000),
            TextGenerationParameter.THINKING_BUDGET: Choice(
                options=["minimal", "low", "medium", "high"]
            ),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="gpt-5.1",
        provider=Provider.OPENAI,
        display_name="GPT-5.1",
        streaming=True,
        parameter_constraints={
            Parameter.MAX_TOKENS: Range(min=1, max=128000),
            TextGenerationParameter.THINKING_BUDGET: Choice(
                options=["minimal", "low", "medium", "high"]
            ),
            TextGenerationParameter.VERBOSITY: Choice(
                options=["low", "medium", "high"]
            ),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="gpt-5.1-codex",
        provider=Provider.OPENAI,
        display_name="GPT-5.1 Codex",
        streaming=True,
        parameter_constraints={
            Parameter.MAX_TOKENS: Range(min=1, max=128000),
            TextGenerationParameter.THINKING_BUDGET: Choice(
                options=["minimal", "low", "medium", "high"]
            ),
            TextGenerationParameter.VERBOSITY: Choice(
                options=["low", "medium", "high"]
            ),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="gpt-5-mini",
        provider=Provider.OPENAI,
        display_name="GPT-5 Mini",
        streaming=True,
        parameter_constraints={
            Parameter.MAX_TOKENS: Range(min=1, max=128000),
            TextGenerationParameter.THINKING_BUDGET: Choice(
                options=["minimal", "low", "medium", "high"]
            ),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="gpt-5-nano",
        provider=Provider.OPENAI,
        display_name="GPT-5 Nano",
        streaming=True,
        parameter_constraints={
            Parameter.MAX_TOKENS: Range(min=1, max=128000),
            TextGenerationParameter.THINKING_BUDGET: Choice(
                options=["minimal", "low", "medium", "high"]
            ),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="gpt-4.1",
        provider=Provider.OPENAI,
        display_name="GPT-4.1",
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=32768),
            TextGenerationParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
]
