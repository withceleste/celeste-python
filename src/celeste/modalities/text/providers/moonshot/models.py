"""Moonshot models for text modality."""

from celeste.constraints import ImagesConstraint, Range, Schema
from celeste.core import Modality, Operation, Parameter, Provider
from celeste.models import Model

from ...parameters import TextParameter

MODELS: list[Model] = [
    Model(
        id="moonshot-v1-8k-vision-preview",
        provider=Provider.MOONSHOT,
        display_name="Moonshot v1 8K Vision (Preview)",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=1.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=8192, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
    Model(
        id="kimi-k2-0905-preview",
        provider=Provider.MOONSHOT,
        display_name="Kimi K2 (0905 Preview)",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=1.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="kimi-k2-0711-preview",
        provider=Provider.MOONSHOT,
        display_name="Kimi K2 (0711 Preview)",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=1.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="kimi-k2-turbo-preview",
        provider=Provider.MOONSHOT,
        display_name="Kimi K2 Turbo Preview",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=1.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="kimi-k2-thinking-turbo",
        provider=Provider.MOONSHOT,
        display_name="Kimi K2 Thinking Turbo",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=1.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="kimi-k2-thinking",
        provider=Provider.MOONSHOT,
        display_name="Kimi K2 Thinking",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=1.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
]
