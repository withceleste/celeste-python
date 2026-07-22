"""Google models for text modality."""

from celeste.constraints import (
    AudioConstraint,
    Choice,
    DocumentsConstraint,
    ImagesConstraint,
    Range,
    Schema,
    ToolChoiceSupport,
    ToolSupport,
    VideosConstraint,
)
from celeste.core import Modality, Operation, Parameter, Provider
from celeste.models import Model
from celeste.tools import CodeExecution, UrlContext, WebSearch

from ...parameters import TextParameter

MODELS: list[Model] = [
    Model(
        id="gemini-2.5-flash",
        provider=Provider.GOOGLE,
        display_name="Gemini 2.5 Flash",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=65536),
            # Flash: allows -1 (dynamic), 0 (disable), or >= 0
            TextParameter.THINKING_BUDGET: Range(min=-1, max=24576),
            TextParameter.TOOLS: ToolSupport(
                tools=[WebSearch, CodeExecution, UrlContext]
            ),
            TextParameter.TOOL_CHOICE: ToolChoiceSupport(),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            # Media input support
            TextParameter.IMAGE: ImagesConstraint(),
            TextParameter.VIDEO: VideosConstraint(),
            TextParameter.AUDIO: AudioConstraint(),
            TextParameter.DOCUMENT: DocumentsConstraint(),
        },
    ),
    Model(
        id="gemini-2.5-flash-lite",
        provider=Provider.GOOGLE,
        display_name="Gemini 2.5 Flash Lite",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=65536),
            # Flash Lite: allows -1 (dynamic), 0 (disable), or >= 512
            TextParameter.THINKING_BUDGET: Range(
                min=512, max=24576, special_values=[-1, 0]
            ),
            TextParameter.TOOLS: ToolSupport(
                tools=[WebSearch, CodeExecution, UrlContext]
            ),
            TextParameter.TOOL_CHOICE: ToolChoiceSupport(),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            # Media input support
            TextParameter.IMAGE: ImagesConstraint(),
            TextParameter.VIDEO: VideosConstraint(),
            TextParameter.AUDIO: AudioConstraint(),
            TextParameter.DOCUMENT: DocumentsConstraint(),
        },
    ),
    Model(
        id="gemini-2.5-pro",
        provider=Provider.GOOGLE,
        display_name="Gemini 2.5 Pro",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=65536),
            # Pro: allows -1 (dynamic) or >= 128 (cannot use 0)
            TextParameter.THINKING_BUDGET: Range(
                min=128, max=32768, special_values=[-1]
            ),
            TextParameter.TOOLS: ToolSupport(
                tools=[WebSearch, CodeExecution, UrlContext]
            ),
            TextParameter.TOOL_CHOICE: ToolChoiceSupport(),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            # Media input support
            TextParameter.IMAGE: ImagesConstraint(),
            TextParameter.VIDEO: VideosConstraint(),
            TextParameter.AUDIO: AudioConstraint(),
            TextParameter.DOCUMENT: DocumentsConstraint(),
        },
    ),
    Model(
        id="gemini-3-flash-preview",
        provider=Provider.GOOGLE,
        display_name="Gemini 3 Flash",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=65536),
            TextParameter.THINKING_LEVEL: Choice(
                options=["minimal", "low", "medium", "high"]
            ),
            TextParameter.TOOLS: ToolSupport(
                tools=[WebSearch, CodeExecution, UrlContext]
            ),
            TextParameter.TOOL_CHOICE: ToolChoiceSupport(),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            # Media input support
            TextParameter.IMAGE: ImagesConstraint(),
            TextParameter.VIDEO: VideosConstraint(),
            TextParameter.AUDIO: AudioConstraint(),
            TextParameter.DOCUMENT: DocumentsConstraint(),
        },
    ),
    Model(
        id="gemini-3.1-pro-preview",
        provider=Provider.GOOGLE,
        display_name="Gemini 3.1 Pro",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=65536),
            TextParameter.THINKING_LEVEL: Choice(options=["low", "medium", "high"]),
            TextParameter.TOOLS: ToolSupport(
                tools=[WebSearch, CodeExecution, UrlContext]
            ),
            TextParameter.TOOL_CHOICE: ToolChoiceSupport(),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            # Media input support
            TextParameter.IMAGE: ImagesConstraint(),
            TextParameter.VIDEO: VideosConstraint(),
            TextParameter.AUDIO: AudioConstraint(),
            TextParameter.DOCUMENT: DocumentsConstraint(),
        },
    ),
    Model(
        id="gemini-3.1-flash-lite",
        provider=Provider.GOOGLE,
        display_name="Gemini 3.1 Flash Lite",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=65536),
            TextParameter.THINKING_LEVEL: Choice(
                options=["minimal", "low", "medium", "high"]
            ),
            TextParameter.TOOLS: ToolSupport(
                tools=[WebSearch, CodeExecution, UrlContext]
            ),
            TextParameter.TOOL_CHOICE: ToolChoiceSupport(),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            # Media input support
            TextParameter.IMAGE: ImagesConstraint(),
            TextParameter.VIDEO: VideosConstraint(),
            TextParameter.AUDIO: AudioConstraint(),
            TextParameter.DOCUMENT: DocumentsConstraint(),
        },
    ),
    Model(
        id="gemini-3.5-flash",
        provider=Provider.GOOGLE,
        display_name="Gemini 3.5 Flash",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0),
            Parameter.MAX_TOKENS: Range(min=1, max=65536),
            TextParameter.THINKING_LEVEL: Choice(
                options=["minimal", "low", "medium", "high"]
            ),
            TextParameter.TOOLS: ToolSupport(
                tools=[WebSearch, CodeExecution, UrlContext]
            ),
            TextParameter.TOOL_CHOICE: ToolChoiceSupport(),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            # Media input support
            TextParameter.IMAGE: ImagesConstraint(),
            TextParameter.VIDEO: VideosConstraint(),
            TextParameter.AUDIO: AudioConstraint(),
            TextParameter.DOCUMENT: DocumentsConstraint(),
        },
    ),
    Model(
        id="gemini-3.5-flash-lite",
        provider=Provider.GOOGLE,
        display_name="Gemini 3.5 Flash Lite",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.MAX_TOKENS: Range(min=1, max=65536),
            TextParameter.THINKING_LEVEL: Choice(
                options=["minimal", "low", "medium", "high"]
            ),
            TextParameter.TOOLS: ToolSupport(
                tools=[WebSearch, CodeExecution, UrlContext]
            ),
            TextParameter.TOOL_CHOICE: ToolChoiceSupport(),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            # Media input support
            TextParameter.IMAGE: ImagesConstraint(),
            TextParameter.VIDEO: VideosConstraint(),
            TextParameter.AUDIO: AudioConstraint(),
            TextParameter.DOCUMENT: DocumentsConstraint(),
        },
    ),
    Model(
        id="gemini-3.6-flash",
        provider=Provider.GOOGLE,
        display_name="Gemini 3.6 Flash",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.MAX_TOKENS: Range(min=1, max=65536),
            TextParameter.THINKING_LEVEL: Choice(
                options=["minimal", "low", "medium", "high"]
            ),
            TextParameter.TOOLS: ToolSupport(
                tools=[WebSearch, CodeExecution, UrlContext]
            ),
            TextParameter.TOOL_CHOICE: ToolChoiceSupport(),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            # Media input support
            TextParameter.IMAGE: ImagesConstraint(),
            TextParameter.VIDEO: VideosConstraint(),
            TextParameter.AUDIO: AudioConstraint(),
            TextParameter.DOCUMENT: DocumentsConstraint(),
        },
    ),
]
