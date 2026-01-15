"""Google models for embeddings modality."""

from celeste.constraints import Choice
from celeste.core import Modality, Operation, Provider
from celeste.models import Model

from ...parameters import EmbeddingsParameter

MODELS: list[Model] = [
    Model(
        id="gemini-embedding-001",
        provider=Provider.GOOGLE,
        display_name="Gemini Embedding 001",
        operations={Modality.EMBEDDINGS: {Operation.EMBED}},
        parameter_constraints={
            EmbeddingsParameter.DIMENSIONS: Choice(options=[768, 1536, 3072]),
        },
    ),
]
