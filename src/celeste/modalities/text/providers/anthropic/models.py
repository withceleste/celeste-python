"""Anthropic models for text modality."""

from celeste.constraints import ImagesConstraint, Range, Schema
from celeste.core import Modality, Operation, Parameter, Provider
from celeste.models import Model

from ...parameters import TextParameter

MODELS: list[Model] = [
    Model(
        id="claude-sonnet-4-5",
        provider=Provider.ANTHROPIC,
        display_name="Claude Sonnet 4.5",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.MAX_TOKENS: Range(min=1, max=64000),
            TextParameter.THINKING_BUDGET: Range(min=-1, max=64000),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
    Model(
        id="claude-haiku-4-5",
        provider=Provider.ANTHROPIC,
        display_name="Claude Haiku 4.5",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.MAX_TOKENS: Range(min=1, max=64000),
            TextParameter.THINKING_BUDGET: Range(min=-1, max=32000),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
    Model(
        id="claude-opus-4-1",
        provider=Provider.ANTHROPIC,
        display_name="Claude Opus 4.1",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.MAX_TOKENS: Range(min=1, max=32000),
            TextParameter.THINKING_BUDGET: Range(min=-1, max=32000),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
    Model(
        id="claude-opus-4-5",
        provider=Provider.ANTHROPIC,
        display_name="Claude Opus 4.5",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.MAX_TOKENS: Range(min=1, max=64000),
            TextParameter.THINKING_BUDGET: Range(min=-1, max=32000),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
    Model(
        id="claude-sonnet-4-20250514",
        provider=Provider.ANTHROPIC,
        display_name="Claude Sonnet 4",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.MAX_TOKENS: Range(min=1, max=64000),
            TextParameter.THINKING_BUDGET: Range(min=-1, max=64000),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
    Model(
        id="claude-opus-4-20250514",
        provider=Provider.ANTHROPIC,
        display_name="Claude Opus 4",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.MAX_TOKENS: Range(min=1, max=32000),
            TextParameter.THINKING_BUDGET: Range(min=-1, max=32000),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
]
