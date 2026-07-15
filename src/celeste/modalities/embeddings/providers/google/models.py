"""Google models for embeddings modality."""

from celeste.constraints import (
    AudiosConstraint,
    ImagesConstraint,
    Range,
    VideosConstraint,
)
from celeste.core import Modality, Operation, Provider
from celeste.models import Model

from ...parameters import EmbeddingsParameter

MODELS: list[Model] = [
    Model(
        id="gemini-embedding-2",
        provider=Provider.GOOGLE,
        display_name="Gemini Embedding 2",
        operations={Modality.EMBEDDINGS: {Operation.EMBED}},
        parameter_constraints={
            EmbeddingsParameter.DIMENSIONS: Range(min=128, max=3072, step=1),
            EmbeddingsParameter.IMAGE: ImagesConstraint(),
            EmbeddingsParameter.VIDEO: VideosConstraint(),
            EmbeddingsParameter.AUDIO: AudiosConstraint(),
        },
    ),
    Model(
        id="gemini-embedding-2-preview",
        provider=Provider.GOOGLE,
        display_name="Gemini Embedding 2 Preview",
        operations={Modality.EMBEDDINGS: {Operation.EMBED}},
        parameter_constraints={
            EmbeddingsParameter.DIMENSIONS: Range(min=128, max=3072, step=1),
            EmbeddingsParameter.IMAGE: ImagesConstraint(),
            EmbeddingsParameter.VIDEO: VideosConstraint(),
            EmbeddingsParameter.AUDIO: AudiosConstraint(),
        },
    ),
]
