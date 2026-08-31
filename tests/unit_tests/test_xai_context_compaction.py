"""xAI Responses context-compaction contracts."""

from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import AsyncMock, patch

from pydantic import SecretStr

from celeste import Message, Model, Role
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.modalities.text.io import TextInput
from celeste.modalities.text.protocols.openresponses.client import (
    OpenResponsesTextClient,
)
from celeste.modalities.text.providers.xai.client import XAITextClient, XAITextStream
from celeste.modalities.text.providers.xai.io import XAITextOutput, XAITextUsage
from celeste.providers.xai.responses.config import XAIResponsesEndpoint

COMPACTION_ITEM = {
    "type": "compaction",
    "id": "cmp_123",
    "encrypted_content": "opaque-content",
}

COMPACTION_RESPONSE: dict[str, Any] = {
    "id": "cmp_123",
    "object": "response.compaction",
    "created_at": 1_788_000_000,
    "model": "grok-4.6",
    "output": [COMPACTION_ITEM],
    "usage": {
        "input_tokens": 12_000,
        "input_tokens_details": {"cached_tokens": 300},
        "output_tokens": 800,
        "output_tokens_details": {"reasoning_tokens": 240},
        "total_tokens": 12_800,
        "dropped_message_count": 45,
    },
}


def _model(provider: Provider = Provider.XAI) -> Model:
    return Model(
        id="grok-4.6",
        provider=provider,
        display_name="Grok 4.6",
        operations={Modality.TEXT: {Operation.GENERATE}},
    )


def _client() -> XAITextClient:
    return XAITextClient(
        model=_model(),
        provider=Provider.XAI,
        auth=AuthHeader(secret=SecretStr("test")),
    )


async def _async_iter(items: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
    for item in items:
        yield item


async def test_compact_uses_xai_endpoint_and_preserves_usage_and_item() -> None:
    client = _client()
    make_request = AsyncMock(return_value=COMPACTION_RESPONSE)

    with patch.object(XAITextClient, "_make_request", new=make_request):
        output = await client.compact(
            messages=[Message(role=Role.USER, content="Long conversation")]
        )

    assert make_request.await_args is not None
    request = make_request.await_args.args[0]
    assert request == {
        "input": [{"role": "user", "content": "Long conversation"}],
        "model": "grok-4.6",
    }
    assert (
        make_request.await_args.kwargs["endpoint"]
        == XAIResponsesEndpoint.COMPACT_RESPONSE
    )
    assert isinstance(output, XAITextOutput)
    assert output.content == ""
    assert output.signature == COMPACTION_RESPONSE["output"]
    assert output.usage.dropped_message_count == 45
    assert output.model_dump()["usage"]["dropped_message_count"] == 45
    assert "output" not in output.metadata["raw_response"]
    assert output.metadata["raw_response"]["usage"]["dropped_message_count"] == 45


async def test_full_compaction_output_replays_at_head_and_can_recompact() -> None:
    client = _client()
    make_request = AsyncMock(return_value=COMPACTION_RESPONSE)

    with patch.object(XAITextClient, "_make_request", new=make_request):
        compacted = await client.compact("Long conversation")

        followup = client._init_request(
            TextInput(
                messages=[
                    compacted.message,
                    Message(role=Role.USER, content="What gives particles mass?"),
                ]
            )
        )
        assert followup["input"] == [
            *COMPACTION_RESPONSE["output"],
            {"role": "user", "content": "What gives particles mass?"},
        ]

        await client.compact(messages=[compacted.message])

    recompact_request = make_request.await_args_list[1].args[0]
    assert recompact_request["input"] == COMPACTION_RESPONSE["output"]


def test_compact_is_available_synchronously() -> None:
    client = _client()
    make_request = AsyncMock(return_value=COMPACTION_RESPONSE)

    with patch.object(XAITextClient, "_make_request", new=make_request):
        output = client.sync.compact("Long conversation")

    assert output.signature == COMPACTION_RESPONSE["output"]


async def test_xai_unary_and_stream_outputs_use_provider_usage_types() -> None:
    client = _client()
    unary_response = {
        **COMPACTION_RESPONSE,
        "object": "response",
        "status": "completed",
        "output": [
            {
                "type": "message",
                "status": "completed",
                "content": [{"type": "output_text", "text": "done"}],
            }
        ],
    }
    make_request = AsyncMock(return_value=unary_response)

    with patch.object(XAITextClient, "_make_request", new=make_request):
        unary = await client.generate("hello")

    events = [
        {"type": "response.output_text.delta", "delta": "done"},
        {"type": "response.completed", "response": unary_response},
    ]
    stream = XAITextStream(_async_iter(events))
    async for _ in stream:
        pass

    assert isinstance(unary, XAITextOutput)
    assert isinstance(unary.usage, XAITextUsage)
    assert isinstance(stream.output, XAITextOutput)
    assert isinstance(stream.output.usage, XAITextUsage)


def test_shared_openresponses_does_not_capture_xai_compaction_item() -> None:
    client = OpenResponsesTextClient(
        model=_model(Provider.OPENAI),
        provider=Provider.OPENAI,
        auth=AuthHeader(secret=SecretStr("test")),
    )

    assert client._parse_reasoning(COMPACTION_RESPONSE) == (None, [])
