"""Moonshot models for text modality."""

from celeste.constraints import (
    Choice,
    ImagesConstraint,
    Range,
    Schema,
    ToolChoiceSupport,
    ToolSupport,
    VideosConstraint,
)
from celeste.core import Modality, Operation, Parameter, Provider
from celeste.models import Model
from celeste.tools import ToolChoice

from ...parameters import TextParameter

MODELS: list[Model] = [
    Model(
        id="kimi-k3",
        provider=Provider.MOONSHOT,
        display_name="Kimi K3",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.MAX_TOKENS: Range(min=1, max=1_048_576, step=1),
            TextParameter.THINKING_LEVEL: Choice(options=["max"]),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.IMAGE: ImagesConstraint(),
            TextParameter.TOOLS: ToolSupport(tools=[]),
            TextParameter.TOOL_CHOICE: ToolChoiceSupport(),
        },
    ),
    Model(
        id="kimi-k2.6",
        provider=Provider.MOONSHOT,
        display_name="Kimi K2.6",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.IMAGE: ImagesConstraint(),
            TextParameter.VIDEO: VideosConstraint(),
            TextParameter.TOOLS: ToolSupport(tools=[]),
            TextParameter.TOOL_CHOICE: Choice(
                options=[ToolChoice.AUTO, ToolChoice.NONE]
            ),
        },
    ),
    Model(
        id="kimi-k2.7-code",
        provider=Provider.MOONSHOT,
        display_name="Kimi K2.7 Code",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.IMAGE: ImagesConstraint(),
            TextParameter.VIDEO: VideosConstraint(),
            TextParameter.TOOLS: ToolSupport(tools=[]),
            TextParameter.TOOL_CHOICE: Choice(
                options=[ToolChoice.AUTO, ToolChoice.NONE]
            ),
        },
    ),
    Model(
        id="kimi-k2.7-code-highspeed",
        provider=Provider.MOONSHOT,
        display_name="Kimi K2.7 Code Highspeed",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.IMAGE: ImagesConstraint(),
            TextParameter.VIDEO: VideosConstraint(),
            TextParameter.TOOLS: ToolSupport(tools=[]),
            TextParameter.TOOL_CHOICE: Choice(
                options=[ToolChoice.AUTO, ToolChoice.NONE]
            ),
        },
    ),
]
