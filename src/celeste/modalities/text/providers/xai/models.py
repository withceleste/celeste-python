"""xAI models for text modality."""

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
        id="grok-4-1-fast-reasoning",
        provider=Provider.XAI,
        display_name="Grok 4.1 Fast Reasoning",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=30000),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.WEB_SEARCH: Bool(),
            TextParameter.X_SEARCH: Bool(),
            TextParameter.CODE_EXECUTION: Bool(),
        },
    ),
    Model(
        id="grok-4-1-fast-non-reasoning",
        provider=Provider.XAI,
        display_name="Grok 4.1 Fast Non-Reasoning",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=30000),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.WEB_SEARCH: Bool(),
            TextParameter.X_SEARCH: Bool(),
            TextParameter.CODE_EXECUTION: Bool(),
        },
    ),
    Model(
        id="grok-4-fast-reasoning",
        provider=Provider.XAI,
        display_name="Grok 4 Fast Reasoning",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=30000),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.WEB_SEARCH: Bool(),
            TextParameter.X_SEARCH: Bool(),
            TextParameter.CODE_EXECUTION: Bool(),
        },
    ),
    Model(
        id="grok-4-fast-non-reasoning",
        provider=Provider.XAI,
        display_name="Grok 4 Fast Non-Reasoning",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=30000),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.WEB_SEARCH: Bool(),
            TextParameter.X_SEARCH: Bool(),
            TextParameter.CODE_EXECUTION: Bool(),
        },
    ),
    Model(
        id="grok-4-0709",
        provider=Provider.XAI,
        display_name="Grok 4",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=64000),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.WEB_SEARCH: Bool(),
            TextParameter.X_SEARCH: Bool(),
            TextParameter.CODE_EXECUTION: Bool(),
        },
    ),
    Model(
        id="grok-3-mini",
        provider=Provider.XAI,
        display_name="Grok 3 Mini",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=16000),
            TextParameter.THINKING_BUDGET: Choice(options=["low", "high"]),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.WEB_SEARCH: Bool(),
            TextParameter.X_SEARCH: Bool(),
            TextParameter.CODE_EXECUTION: Bool(),
        },
    ),
    Model(
        id="grok-2-vision-1212",
        provider=Provider.XAI,
        display_name="Grok 2 Vision",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=32768),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
]
