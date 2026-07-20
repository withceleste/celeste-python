"""Tests for Celeste's domain-to-modality routing."""

import pytest

from celeste.core import Domain, Modality, Operation, infer_modality


@pytest.mark.parametrize(
    ("domain", "operation", "expected"),
    [
        (Domain.TEXT, Operation.GENERATE, Modality.TEXT),
        (Domain.TEXT, Operation.EMBED, Modality.EMBEDDINGS),
        (Domain.IMAGES, Operation.ANALYZE, Modality.TEXT),
        (Domain.IMAGES, Operation.EDIT, Modality.IMAGES),
        (Domain.AUDIO, Operation.GENERATE, Modality.AUDIO),
        (Domain.AUDIO, Operation.SPEAK, Modality.AUDIO),
        (Domain.VIDEOS, Operation.GENERATE, Modality.VIDEOS),
        (Domain.DOCUMENTS, Operation.ANALYZE, Modality.TEXT),
    ],
)
def test_infer_modality(
    domain: Domain, operation: Operation, expected: Modality
) -> None:
    assert infer_modality(domain, operation) is expected


def test_infer_modality_rejects_unsupported_pair() -> None:
    with pytest.raises(
        ValueError,
        match="No modality mapping for domain=documents, operation=generate",
    ):
        infer_modality(Domain.DOCUMENTS, Operation.GENERATE)
