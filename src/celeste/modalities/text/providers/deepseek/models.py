"""DeepSeek models for text modality."""

from celeste.constraints import Range, Schema
from celeste.core import Modality, Operation, Parameter, Provider
from celeste.models import Model

from ...parameters import TextParameter

MODELS: list[Model] = [
    Model(
        id="deepseek-chat",
        provider=Provider.DEEPSEEK,
        display_name="DeepSeek Chat",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=8192, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="deepseek-reasoner",
        provider=Provider.DEEPSEEK,
        display_name="DeepSeek Reasoner",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=65536, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
]
