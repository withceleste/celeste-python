"""Meta models for text modality."""

from celeste.constraints import (
    Choice,
    DocumentsConstraint,
    ImagesConstraint,
    Range,
    Schema,
    ToolSupport,
)
from celeste.core import Modality, Operation, Parameter, Provider
from celeste.models import Model
from celeste.tools import WebSearch

from ...parameters import TextParameter

MODELS: list[Model] = [
    Model(
        id="muse-wonder-1.0",
        provider=Provider.META,
        display_name="Muse Wonder",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            TextParameter.THINKING_LEVEL: Choice(
                options=["minimal", "low", "medium", "high", "xhigh", "max"]
            ),
            TextParameter.TOOLS: ToolSupport(tools=[WebSearch]),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.IMAGE: ImagesConstraint(),
            TextParameter.DOCUMENT: DocumentsConstraint(),
        },
    ),
    Model(
        id="muse-spark-1.3",
        provider=Provider.META,
        display_name="Muse Spark 1.3",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            TextParameter.THINKING_LEVEL: Choice(
                options=["minimal", "low", "medium", "high", "xhigh", "max"]
            ),
            TextParameter.TOOLS: ToolSupport(tools=[WebSearch]),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.IMAGE: ImagesConstraint(),
            TextParameter.DOCUMENT: DocumentsConstraint(),
        },
    ),
    Model(
        id="muse-spark-1.3-contributor",
        provider=Provider.META,
        display_name="Muse Spark 1.3 Contributor",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            TextParameter.THINKING_LEVEL: Choice(
                options=["minimal", "low", "medium", "high", "xhigh", "max"]
            ),
            TextParameter.TOOLS: ToolSupport(tools=[WebSearch]),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.IMAGE: ImagesConstraint(),
            TextParameter.DOCUMENT: DocumentsConstraint(),
        },
    ),
]
