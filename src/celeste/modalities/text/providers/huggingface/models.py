"""HuggingFace models for text modality."""

from celeste.constraints import Range, Schema, ToolSupport
from celeste.core import Modality, Operation, Parameter, Provider
from celeste.models import Model

from ...parameters import TextParameter

MODELS: list[Model] = [
    Model(
        id="Qwen/Qwen3-4B-Instruct-2507",
        provider=Provider.HUGGINGFACE,
        display_name="Qwen 3 4B Instruct",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.TOOLS: ToolSupport(tools=[]),
        },
    ),
]
