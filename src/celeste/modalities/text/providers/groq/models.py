"""Groq models for text modality."""

from celeste.constraints import ImagesConstraint, Range, Schema
from celeste.core import Modality, Operation, Parameter, Provider
from celeste.models import Model

from ...parameters import TextParameter

MODELS: list[Model] = [
    Model(
        id="llama-3.3-70b-versatile",
        provider=Provider.GROQ,
        display_name="Llama 3.3 70B Versatile",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=32768, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="llama-3.1-8b-instant",
        provider=Provider.GROQ,
        display_name="Llama 3.1 8B Instant",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=131072, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="qwen/qwen3-32b",
        provider=Provider.GROQ,
        display_name="Qwen 3 32B",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=40960, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="moonshotai/kimi-k2-instruct",
        provider=Provider.GROQ,
        display_name="Kimi K2 Instruct",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=16384, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="moonshotai/kimi-k2-instruct-0905",
        provider=Provider.GROQ,
        display_name="Kimi K2 Instruct 0905",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=16384, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="meta-llama/llama-4-scout-17b-16e-instruct",
        provider=Provider.GROQ,
        display_name="Llama 4 Scout 17B",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=8192, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
    Model(
        id="meta-llama/llama-4-maverick-17b-128e-instruct",
        provider=Provider.GROQ,
        display_name="Llama 4 Maverick 17B",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=8192, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
            TextParameter.IMAGE: ImagesConstraint(),
        },
    ),
    Model(
        id="openai/gpt-oss-20b",
        provider=Provider.GROQ,
        display_name="GPT OSS 20B",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=65536, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="openai/gpt-oss-120b",
        provider=Provider.GROQ,
        display_name="GPT OSS 120B",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=65536, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="openai/gpt-oss-safeguard-20b",
        provider=Provider.GROQ,
        display_name="GPT OSS Safeguard 20B",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=65536, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="groq/compound",
        provider=Provider.GROQ,
        display_name="Groq Compound",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=8192, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="groq/compound-mini",
        provider=Provider.GROQ,
        display_name="Groq Compound Mini",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=8192, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
    Model(
        id="allam-2-7b",
        provider=Provider.GROQ,
        display_name="Allam 2 7B",
        operations={Modality.TEXT: {Operation.GENERATE}},
        streaming=True,
        parameter_constraints={
            Parameter.TEMPERATURE: Range(min=0.0, max=2.0, step=0.01),
            Parameter.MAX_TOKENS: Range(min=1, max=4096, step=1),
            TextParameter.OUTPUT_SCHEMA: Schema(),
        },
    ),
]
