"""Cohere models for text modality."""

from celeste.constraints import ImagesConstraint, Range, Schema
from celeste.core import Modality, Operation, Parameter, Provider
from celeste.models import Model

from ...parameters import TextParameter

MODELS: list[Model] = [
    Model(
        id="command-a-vision-07-2025",
        provider=Provider.COHERE,
        display_name="Command A Vision 07-2025",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=1.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=4096, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
    Model(
        id="command-a-03-2025",
        provider=Provider.COHERE,
        display_name="Command A 03-2025",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=1.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=4096, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            # thinking_budget: Not confirmed for this model, omit constraint
        },
    ),
    Model(
        id="command-r7b-12-2024",
        provider=Provider.COHERE,
        display_name="Command R7B",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=1.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=4096, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            # thinking_budget: Support unclear, omit constraint for now
        },
    ),
]
