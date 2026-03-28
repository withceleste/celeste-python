"""Integration tests for text analyze operation - all document-capable models."""

import warnings

# Suppress deprecation warnings from legacy capability packages
warnings.filterwarnings(
    "ignore",
    message=".*capability parameter is deprecated.*",
    category=DeprecationWarning,
)

import pytest  # noqa: E402

from celeste import (  # noqa: E402
    Modality,
    Model,
    Operation,
    create_client,
    list_models,
)
from celeste.artifacts import DocumentArtifact  # noqa: E402
from celeste.core import InputType  # noqa: E402
from celeste.modalities.text import TextOutput, TextUsage  # noqa: E402

TEST_MAX_TOKENS = 200


@pytest.mark.parametrize(
    "model",
    [
        m
        for m in list_models(modality=Modality.TEXT, operation=Operation.ANALYZE)
        if not m.streaming and InputType.DOCUMENT in m.optional_input_types
    ],
    ids=lambda m: f"{m.provider}-{m.id}",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_analyze(model: Model, test_document: DocumentArtifact) -> None:
    """Test document analysis for all document-capable models.

    Dynamically discovers all document models via list_models() and verifies each
    can analyze documents. Failures indicate deprecated or misconfigured models.
    """
    client = create_client(
        modality=Modality.TEXT,
        model=model,
    )

    response = await client.analyze(
        prompt="Summarize this document",
        document=test_document,
        max_tokens=TEST_MAX_TOKENS,
    )

    assert isinstance(response, TextOutput), (
        f"Expected TextOutput, got {type(response)}"
    )
    # Empty/None content is valid for reasoning models that use all tokens for thinking
    if not response.content:
        assert response.finish_reason is not None, (
            f"Model {model.provider}/{model.id} returned empty content without finish_reason"
        )
    assert isinstance(response.usage, TextUsage), (
        f"Expected TextUsage, got {type(response.usage)}"
    )
    if (
        response.usage.output_tokens is not None
        and response.usage.output_tokens > TEST_MAX_TOKENS
    ):
        warnings.warn(
            f"Model {model.provider}/{model.id} exceeded max_tokens: {response.usage.output_tokens} > {TEST_MAX_TOKENS}",
            stacklevel=1,
        )


@pytest.mark.integration
def test_sync_analyze(test_document: DocumentArtifact) -> None:
    """Test sync wrapper works correctly.

    Single model smoke test - sync is just async_to_sync wrapper.
    """
    models = [
        m
        for m in list_models(modality=Modality.TEXT, operation=Operation.ANALYZE)
        if InputType.DOCUMENT in m.optional_input_types
    ]
    model = models[0]

    client = create_client(
        modality=Modality.TEXT,
        model=model,
    )

    response = client.sync.analyze(
        prompt="Summarize this document",
        document=test_document,
        max_tokens=TEST_MAX_TOKENS,
    )

    assert isinstance(response, TextOutput)
    assert response.content or response.finish_reason is not None
