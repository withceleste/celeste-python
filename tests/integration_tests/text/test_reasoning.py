"""Integration tests for reasoning/thinking content in text generation."""

import warnings

warnings.filterwarnings(
    "ignore",
    message=".*capability parameter is deprecated.*",
    category=DeprecationWarning,
)

import pytest  # noqa: E402

from celeste import Modality, Model, Operation, create_client, list_models  # noqa: E402
from celeste.constraints import Choice, Range  # noqa: E402
from celeste.modalities.text import TextChunk, TextOutput  # noqa: E402
from celeste.modalities.text.parameters import TextParameter  # noqa: E402

# Models that support thinking_budget — one per provider for fast feedback
REASONING_MODELS = [
    m
    for m in list_models(modality=Modality.TEXT, operation=Operation.GENERATE)
    if TextParameter.THINKING_BUDGET in (m.parameter_constraints or {})
]

# Pick one model per provider to avoid slow test matrix
_seen_providers: set[str] = set()
REASONING_MODELS_ONE_PER_PROVIDER = []
for m in REASONING_MODELS:
    if m.provider not in _seen_providers:
        _seen_providers.add(m.provider)
        REASONING_MODELS_ONE_PER_PROVIDER.append(m)


def _get_thinking_budget(model: Model) -> int | str:
    """Get an appropriate thinking_budget value based on the model's constraint type."""
    constraint = (model.parameter_constraints or {}).get(TextParameter.THINKING_BUDGET)
    if isinstance(constraint, Range):
        return 1024
    if isinstance(constraint, Choice):
        return "high" if "high" in constraint.options else constraint.options[-1]
    return 1024


@pytest.mark.parametrize(
    "model",
    REASONING_MODELS_ONE_PER_PROVIDER,
    ids=lambda m: f"{m.provider}-{m.id}",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_reasoning_generate(model: Model) -> None:
    """Test that reasoning text is returned when thinking_budget is set."""
    client = create_client(modality=Modality.TEXT, model=model)

    response = await client.generate(
        prompt="What is 15 * 37? Think step by step.",
        max_tokens=2000,
        thinking_budget=_get_thinking_budget(model),
    )

    assert isinstance(response, TextOutput)
    assert response.reasoning is not None, (
        f"Model {model.provider}/{model.id} returned no reasoning"
    )
    assert len(response.reasoning) > 0, (
        f"Model {model.provider}/{model.id} returned empty reasoning"
    )
    assert response.content, (
        f"Model {model.provider}/{model.id} returned no content alongside reasoning"
    )


@pytest.mark.parametrize(
    "model",
    [m for m in REASONING_MODELS_ONE_PER_PROVIDER if m.streaming],
    ids=lambda m: f"{m.provider}-{m.id}",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_reasoning_stream(model: Model) -> None:
    """Test that reasoning chunks are streamed when thinking_budget is set."""
    client = create_client(modality=Modality.TEXT, model=model)

    chunks: list[TextChunk] = []
    async for chunk in client.stream.generate(
        prompt="What is 15 * 37? Think step by step.",
        max_tokens=2000,
        thinking_budget=_get_thinking_budget(model),
    ):
        chunks.append(chunk)

    reasoning_chunks = [c for c in chunks if c.reasoning]
    assert len(reasoning_chunks) > 0, (
        f"Model {model.provider}/{model.id} streamed no reasoning chunks"
    )


@pytest.mark.parametrize(
    "model",
    REASONING_MODELS_ONE_PER_PROVIDER,
    ids=lambda m: f"{m.provider}-{m.id}",
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_reasoning_message_roundtrip(model: Model) -> None:
    """Test that output.message preserves reasoning for multi-turn."""
    client = create_client(modality=Modality.TEXT, model=model)

    response = await client.generate(
        prompt="What is 15 * 37? Think step by step.",
        max_tokens=2000,
        thinking_budget=_get_thinking_budget(model),
    )

    msg = response.message
    assert msg.reasoning is not None, "Message should carry reasoning text"

    # Verify signature data is attached (for providers that need it)
    if response.reasoning and response.signature:
        assert msg.signature is not None, (
            "Message should carry signature for round-trip"
        )
