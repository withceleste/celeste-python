"""xAI Responses native image output, streaming, and continuation."""

import base64
import json
from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import SecretStr

from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import ImageMimeType
from celeste.modalities.text.io import TextInput
from celeste.modalities.text.protocols.openresponses.client import (
    OpenResponsesTextClient,
    OpenResponsesTextStream,
)
from celeste.modalities.text.providers.ollama.client import OllamaTextClient
from celeste.modalities.text.providers.openai.client import OpenAITextClient
from celeste.modalities.text.providers.openrouter.client import OpenRouterTextClient
from celeste.modalities.text.providers.xai.client import XAITextClient, XAITextStream
from celeste.modalities.text.providers.xai.io import XAITextOutput
from celeste.models import Model
from celeste.tools import ToolResult
from celeste.types import (
    ImagePart,
    Message,
    Role,
    TextPart,
    ToolActivity,
    ToolActivityStatus,
)

IMAGE_DATA = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\0" * 20
IMAGE_RESULT = base64.b64encode(IMAGE_DATA).decode()
IMAGE_ITEM = {
    "type": "image_generation_call",
    "id": "ig_first",
    "status": "completed",
    "prompt": "first",
    "result": IMAGE_RESULT,
}
REASONING_ITEM = {
    "type": "reasoning",
    "id": "r_01",
    "summary": [{"type": "summary_text", "text": "Plan."}],
}
OUTPUT_ITEMS = [
    REASONING_ITEM,
    IMAGE_ITEM,
    {
        "type": "message",
        "id": "msg_01",
        "status": "completed",
        "role": "assistant",
        "content": [
            {"type": "output_text", "text": "Between "},
            {"type": "output_text", "text": "images."},
        ],
    },
    {
        "type": "web_search_call",
        "id": "ws_01",
        "status": "completed",
        "action": {"type": "search", "query": "reference"},
    },
    {
        "type": "function_call",
        "id": "fc_01",
        "call_id": "call_01",
        "name": "save",
        "arguments": "{}",
    },
    {**IMAGE_ITEM, "id": "ie_second", "prompt": "second"},
]


def _client(
    client_class: type[OpenResponsesTextClient] = XAITextClient,
) -> OpenResponsesTextClient:
    return client_class(
        model=Model(
            id="grok-4.6",
            provider=Provider.XAI,
            display_name="Grok 4.6",
            operations={Modality.TEXT: {Operation.GENERATE}},
            streaming=True,
        ),
        provider=Provider.XAI,
        auth=AuthHeader(secret=SecretStr("test")),
    )


async def _async_iter(items: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
    for item in items:
        yield item


@pytest.mark.parametrize("image_only", [False, True])
async def test_image_output_unary_stream_and_replay_parity(image_only: bool) -> None:
    output_items = [IMAGE_ITEM] if image_only else OUTPUT_ITEMS
    response = {
        "id": "resp_01",
        "status": "completed",
        "output": output_items,
        "usage": {
            "input_tokens": 10,
            "output_tokens": 5,
            "total_tokens": 15,
            "cost_in_usd_ticks": 12345,
        },
    }
    client = _client()
    with patch.object(XAITextClient, "_make_request", AsyncMock(return_value=response)):
        unary = await client.generate("Make an image")

    events: list[dict[str, Any]] = []
    if not image_only:
        events.extend(
            [
                {"type": "response.reasoning_summary_text.delta", "delta": "Plan."},
                {"type": "response.output_text.delta", "delta": "Between images."},
            ]
        )
    events.extend(
        [
            {"type": "response.image_generation_call.in_progress"},
            {"type": "response.image_generation_call.generating"},
            {"type": "response.image_generation_call.completed"},
            {"type": "response.output_item.done", "item": IMAGE_ITEM},
            {"type": "response.completed", "response": response},
        ]
    )
    stream = XAITextStream(_async_iter(events))
    chunks = [chunk async for chunk in stream]

    assert isinstance(unary, XAITextOutput)
    assert isinstance(stream.output, XAITextOutput)
    assert unary.content == stream.output.content
    assert unary.signature == stream.output.signature == output_items
    assert unary.reasoning == stream.output.reasoning
    assert unary.tool_calls == stream.output.tool_calls
    assert unary.finish_reason == stream.output.finish_reason
    assert unary.finish_reason is not None
    assert unary.finish_reason.reason == "completed"
    assert unary.usage == stream.output.usage
    assert (
        unary.metadata["raw_response"]["usage"]
        == (stream.output.metadata["raw_response"]["usage"])
    )
    assert [chunk.tool_activity for chunk in chunks if chunk.tool_activity] == [
        ToolActivity(tool_name="generate_image", status=ToolActivityStatus.STARTED),
        ToolActivity(tool_name="generate_image", status=ToolActivityStatus.COMPLETED),
    ]

    assert isinstance(unary.content, list)
    assert [type(part) for part in unary.content] == (
        [ImagePart] if image_only else [ImagePart, TextPart, TextPart, ImagePart]
    )
    image = unary.content[0]
    assert isinstance(image, ImagePart)
    assert image.image.data == IMAGE_DATA
    assert image.image.mime_type == ImageMimeType.JPEG
    assert image.image.metadata == {
        k: v for k, v in IMAGE_ITEM.items() if k != "result"
    }
    assert unary.message.content == unary.content
    restored = XAITextOutput.model_validate_json(unary.model_dump_json())
    assert restored.content == unary.content
    assert restored.message == unary.message

    followup = client._init_request(
        TextInput(
            messages=[
                restored.message,
                ToolResult(content="saved", tool_call_id="call_01"),
                Message(role=Role.USER, content="Edit the image"),
            ]
        )
    )
    assert followup["input"] == [
        *output_items,
        {"type": "function_call_output", "call_id": "call_01", "output": "saved"},
        {"role": "user", "content": "Edit the image"},
    ]


@pytest.mark.parametrize("result", [None, "", "not base64!", "é"])
def test_missing_or_invalid_image_result_is_rejected(result: object) -> None:
    with pytest.raises(ValueError, match="image_generation_call result"):
        _client()._parse_content({"output": [{**IMAGE_ITEM, "result": result}]})


def test_unknown_image_format_keeps_mime_unset() -> None:
    content = _client()._parse_content(
        {"output": [{**IMAGE_ITEM, "result": base64.b64encode(b"unknown").decode()}]}
    )
    assert isinstance(content, list)
    image = content[0]
    assert isinstance(image, ImagePart)
    assert image.image.mime_type is None


@pytest.mark.parametrize(
    "client_class",
    [OpenResponsesTextClient, OpenAITextClient, OpenRouterTextClient, OllamaTextClient],
)
def test_other_responses_clients_keep_existing_parsing(
    client_class: type[OpenResponsesTextClient],
) -> None:
    client = _client(client_class)
    response = {"output": OUTPUT_ITEMS}
    assert client._parse_content(response) == "Between "
    assert client._parse_reasoning(response) == ("Plan.", [REASONING_ITEM])
    stream = object.__new__(OpenResponsesTextStream)
    assert (
        stream._parse_chunk_tool_activity(
            {"type": "response.image_generation_call.in_progress"}
        )
        is None
    )


def test_structured_json_is_not_interpreted_as_message_parts() -> None:
    content = [{"type": "text", "text": "structured JSON"}]
    output = XAITextOutput(content=content)
    restored = XAITextOutput.model_validate_json(output.model_dump_json())
    assert restored.content == content
    assert restored.message.content == json.dumps(content)


def test_native_image_tool_remains_an_explicit_raw_tool() -> None:
    tool = {"type": "image_generation"}
    request = _client()._build_request(TextInput(prompt="Make an image"), tools=[tool])
    assert request["input"] == "Make an image"
    assert request["tools"] == [tool]
