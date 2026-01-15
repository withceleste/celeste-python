"""Integration tests for text generate operation - all registered models."""

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
from celeste.modalities.text import TextOutput, TextUsage  # noqa: E402

TEST_MAX_TOKENS = 200


@pytest.mark.parametrize(
    "model",
    [
        m
        for m in list_models(modality=Modality.TEXT, operation=Operation.GENERATE)
        if not m.streaming  # Streaming models tested in test_stream_generate
        and not m.optional_input_types  # Media-capable models tested in test_analyze_*
    ],
    ids=lambda m: f"{m.provider.value}-{m.id}",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_generate(model: Model) -> None:
    """Test text generation for all registered models.

    Dynamically discovers all models via list_models() and verifies each one
    can generate text. Failures indicate deprecated or misconfigured models.
    """
    client = create_client(
        modality=Modality.TEXT,
        model=model,
    )

    response = await client.generate(prompt="Hi", max_tokens=TEST_MAX_TOKENS)

    assert isinstance(response, TextOutput), (
        f"Expected TextOutput, got {type(response)}"
    )
    # Empty/None content is valid for reasoning models that use all tokens for thinking
    if not response.content:
        assert response.finish_reason is not None, (
            f"Model {model.provider.value}/{model.id} returned empty content without finish_reason"
        )
    assert isinstance(response.usage, TextUsage), (
        f"Expected TextUsage, got {type(response.usage)}"
    )
    if (
        response.usage.output_tokens is not None
        and response.usage.output_tokens > TEST_MAX_TOKENS
    ):
        warnings.warn(
            f"Model {model.provider.value}/{model.id} exceeded max_tokens: {response.usage.output_tokens} > {TEST_MAX_TOKENS}",
            stacklevel=1,
        )


@pytest.mark.integration
def test_sync_generate() -> None:
    """Test sync wrapper works correctly.

    Single model smoke test - sync is just async_to_sync wrapper.
    """
    models = list_models(modality=Modality.TEXT, operation=Operation.GENERATE)
    model = models[0]

    client = create_client(
        modality=Modality.TEXT,
        model=model,
    )

    response = client.sync.generate(prompt="Hi", max_tokens=TEST_MAX_TOKENS)

    assert isinstance(response, TextOutput)
    assert response.content or response.finish_reason is not None
