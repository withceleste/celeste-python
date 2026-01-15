"""OpenAI models for text modality."""

from celeste.constraints import (
    Bool,
    Choice,
    ImagesConstraint,
    Range,
    Schema,
)
from celeste.core import Modality, Operation, Parameter, Provider
from celeste.models import Model

from ...parameters import TextParameter

MODELS: list[Model] = [
    Model(
        id="gpt-4o",
        provider=Provider.OPENAI,
        display_name="GPT-4o",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=16384),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.WEB_SEARCH: Bool(),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
    Model(
        id="gpt-4o-mini",
        provider=Provider.OPENAI,
        display_name="GPT-4o Mini",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=16384),
            TextParameter.WEB_SEARCH: Bool(),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
    Model(
        id="gpt-4-turbo",
        provider=Provider.OPENAI,
        display_name="GPT-4 Turbo",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=4096),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
    Model(
        id="gpt-4",
        provider=Provider.OPENAI,
        display_name="GPT-4",
        operations={Modality.TEXT: {Operation.GENERATE}},
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
        operations={Modality.TEXT: {Operation.GENERATE}},
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
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.MAX_TOKENS: Range(min=1, max=128000),
            TextParameter.THINKING_BUDGET: Choice(
                options=["minimal", "low", "medium", "high"]
            ),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.WEB_SEARCH: Bool(),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
    Model(
        id="gpt-5.2",
        provider=Provider.OPENAI,
        display_name="GPT-5.2",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.MAX_TOKENS: Range(min=1, max=128000),
            TextParameter.THINKING_BUDGET: Choice(
                options=["minimal", "low", "medium", "high", "xhigh"]
            ),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.WEB_SEARCH: Bool(),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
    Model(
        id="gpt-5.2-pro",
        provider=Provider.OPENAI,
        display_name="GPT-5.2 Pro",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.MAX_TOKENS: Range(min=1, max=128000),
            TextParameter.THINKING_BUDGET: Choice(
                options=["minimal", "low", "medium", "high", "xhigh"]
            ),
            TextParameter.VERBOSITY: Choice(options=["low", "medium", "high"]),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.WEB_SEARCH: Bool(),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
    Model(
        id="gpt-5.2-codex",
        provider=Provider.OPENAI,
        display_name="GPT-5.2 Codex",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.MAX_TOKENS: Range(min=1, max=128000),
            TextParameter.THINKING_BUDGET: Choice(
                options=["low", "medium", "high", "xhigh"]
            ),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
    Model(
        id="gpt-5.2-chat-latest",
        provider=Provider.OPENAI,
        display_name="GPT-5.2 Instant",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=128000),
            TextParameter.WEB_SEARCH: Bool(),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
    Model(
        id="gpt-5.1",
        provider=Provider.OPENAI,
        display_name="GPT-5.1",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.MAX_TOKENS: Range(min=1, max=128000),
            TextParameter.THINKING_BUDGET: Choice(
                options=["minimal", "low", "medium", "high"]
            ),
            TextParameter.VERBOSITY: Choice(options=["low", "medium", "high"]),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.WEB_SEARCH: Bool(),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
    Model(
        id="gpt-5.1-codex",
        provider=Provider.OPENAI,
        display_name="GPT-5.1 Codex",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.MAX_TOKENS: Range(min=1, max=128000),
            TextParameter.THINKING_BUDGET: Choice(
                options=["minimal", "low", "medium", "high"]
            ),
            TextParameter.VERBOSITY: Choice(options=["low", "medium", "high"]),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.WEB_SEARCH: Bool(),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
    Model(
        id="gpt-5-mini",
        provider=Provider.OPENAI,
        display_name="GPT-5 Mini",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.MAX_TOKENS: Range(min=1, max=128000),
            TextParameter.THINKING_BUDGET: Choice(
                options=["minimal", "low", "medium", "high"]
            ),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.WEB_SEARCH: Bool(),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
    Model(
        id="gpt-5-nano",
        provider=Provider.OPENAI,
        display_name="GPT-5 Nano",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.MAX_TOKENS: Range(min=1, max=128000),
            TextParameter.THINKING_BUDGET: Choice(
                options=["minimal", "low", "medium", "high"]
            ),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.WEB_SEARCH: Bool(),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
    Model(
        id="gpt-4.1",
        provider=Provider.OPENAI,
        display_name="GPT-4.1",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=32768),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.WEB_SEARCH: Bool(),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
]
