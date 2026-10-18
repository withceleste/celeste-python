"""Tool-call arguments are validated at the response boundary."""

import json
from collections.abc import AsyncIterator
from enum import StrEnum
from typing import Any

import pytest
from pydantic import BaseModel

from celeste import (
    Modality,
    Model,
    NoAuth,
    Operation,
    Protocol,
    Provider,
    create_client,
)
from celeste.exceptions import StreamNotExhaustedError, ValidationError
from celeste.io import Chunk, Output
from celeste.modalities.live.providers.openai.client import OpenAILiveStream
from celeste.parameters import Parameters
from celeste.providers.google.auth import GoogleADC
from celeste.streaming import Stream
from celeste.tools import CodeExecution, ToolCall, validate_tool_calls


class ImageId(StrEnum):
    IMG_1 = "img-1"


class AnalyzeImageParams(BaseModel):
    image_id: ImageId


class NullableParams(BaseModel):
    first_frame: None = None


def _tool(parameters: type[BaseModel]) -> dict[str, object]:
    return {"name": "analyze_image", "parameters": parameters}


def test_validation_preserves_normalized_arguments_and_provider_fields() -> None:
    call = ToolCall(
        id="call-1",
        name="analyze_image",
        arguments={"image_id": "img-1"},
        thoughtSignature="sig-1",
    )

    assert validate_tool_calls([call], [_tool(AnalyzeImageParams)]) == [call]
    assert call.thoughtSignature == "sig-1"


@pytest.mark.parametrize(
    ("arguments", "parameters", "match"),
    [
        ({"image_id": "fake"}, AnalyzeImageParams, "fake"),
        ({"first_frame": "img-1"}, NullableParams, "first_frame"),
    ],
)
def test_invalid_arguments_fail(
    arguments: dict[str, object], parameters: type[BaseModel], match: str
) -> None:
    call = ToolCall(id="call-1", name="analyze_image", arguments=arguments)
    with pytest.raises(ValidationError, match=match):
        validate_tool_calls([call], [_tool(parameters)])


@pytest.mark.parametrize("arguments", [{}, {"first_frame": None}])
def test_nullable_argument_accepts_omission_or_null(
    arguments: dict[str, object],
) -> None:
    call = ToolCall(id="call-1", name="analyze_image", arguments=arguments)
    assert validate_tool_calls([call], [_tool(NullableParams)]) == [call]


def test_raw_schema_and_builtin_tools_are_not_locally_validated() -> None:
    call = ToolCall(id="call-1", name="raw_tool", arguments={"anything": "ok"})
    tools = [
        {"name": "raw_tool", "parameters": {"type": "object"}},
        CodeExecution(),
    ]
    assert validate_tool_calls([call], tools) == [call]


class _Stream(Stream[Output[str], Parameters, Chunk[str]]):
    _chunk_class = Chunk[str]
    _output_class = Output[str]
    _empty_content = ""
    returned_tool_calls: list[ToolCall]

    def _aggregate_content(self, chunks: list[Chunk[str]]) -> str:
        return "".join(chunk.content for chunk in chunks)

    def _aggregate_tool_calls(
        self, chunks: list[Chunk[str]], raw_events: list[dict[str, Any]]
    ) -> list[ToolCall]:
        return self.returned_tool_calls


async def _empty_events() -> AsyncIterator[dict[str, Any]]:
    if False:
        yield {}


def test_stream_validates_aggregated_tool_calls() -> None:
    stream = _Stream(_empty_events(), tools=[_tool(AnalyzeImageParams)])
    stream.returned_tool_calls = [
        ToolCall(id="call-1", name="analyze_image", arguments={"image_id": "fake"})
    ]

    with pytest.raises(ValidationError, match="fake"):
        stream._parse_output(
            [Chunk[str](content="ok")], tools=[_tool(AnalyzeImageParams)]
        )


def _tool_only_response(
    family: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    function = {"name": "analyze_image", "arguments": '{"image_id":"img-1"}'}
    if family == "openresponses":
        response = {
            "status": "completed",
            "output": [
                {
                    "type": "function_call",
                    "id": "fc-1",
                    "call_id": "call-1",
                    "status": "completed",
                    **function,
                }
            ],
        }
        return response, [{"type": "response.completed", "response": response}]
    if family == "chatcompletions":
        call = {"id": "call-1", "type": "function", "function": function}
        response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [call],
                    },
                    "finish_reason": "tool_calls",
                }
            ]
        }
        return response, [
            {
                "object": "chat.completion.chunk",
                "choices": [{"delta": {"tool_calls": [{"index": 0, **call}]}}],
            },
            {
                "object": "chat.completion.chunk",
                "choices": [{"delta": {}, "finish_reason": "tool_calls"}],
            },
        ]
    if family == "interactions":
        step = {
            "type": "function_call",
            "id": "call-1",
            "name": "analyze_image",
            "arguments": {"image_id": "img-1"},
        }
        response = {"status": "requires_action", "steps": [step]}
        return response, [
            {
                "event_type": "step.start",
                "index": 0,
                "step": {**step, "arguments": {}},
            },
            {
                "event_type": "step.delta",
                "index": 0,
                "delta": {
                    "type": "arguments_delta",
                    "arguments": function["arguments"],
                },
            },
            {"event_type": "step.stop", "index": 0},
            {"event_type": "interaction.completed", "interaction": response},
        ]
    response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "functionCall": {
                                "id": "call-1",
                                "name": "analyze_image",
                                "args": {"image_id": "img-1"},
                            }
                        }
                    ]
                },
                "finishReason": "STOP",
            }
        ]
    }
    return response, [response]


@pytest.mark.parametrize(
    "family", ["openresponses", "chatcompletions", "interactions", "vertex"]
)
@pytest.mark.parametrize("streaming", [False, True], ids=["unary", "stream"])
async def test_output_schema_preserves_tool_only_turns(
    family: str, streaming: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    google = family in {"interactions", "vertex"}
    client = create_client(
        modality=Modality.TEXT,
        model=Model(
            id="tool-turn",
            display_name="Tool turn",
            provider=Provider.GOOGLE if google else None,
            operations={Modality.TEXT: {Operation.GENERATE}},
            streaming=True,
        ),
        protocol=None if google else Protocol(family),
        auth=GoogleADC(project_id="test-project") if family == "vertex" else NoAuth(),
    )
    response, events = _tool_only_response(family)

    async def make_request(
        _self: object, request_body: dict[str, Any], **_: object
    ) -> dict[str, Any]:
        assert request_body["tools"]
        return response

    async def make_stream_request(
        _self: object, request_body: dict[str, Any], **_: object
    ) -> AsyncIterator[dict[str, Any]]:
        assert request_body["tools"]

        async def iterator() -> AsyncIterator[dict[str, Any]]:
            for event in events:
                yield event

        return iterator()

    monkeypatch.setattr(type(client), "_make_request", make_request)
    monkeypatch.setattr(type(client), "_make_stream_request", make_stream_request)
    tools = [_tool(AnalyzeImageParams)]
    if streaming:
        stream = client.stream.generate(
            "Analyze the image", tools=tools, output_schema=AnalyzeImageParams
        )
        _ = [chunk async for chunk in stream]
        output = stream.output
    else:
        output = await client.generate(
            "Analyze the image", tools=tools, output_schema=AnalyzeImageParams
        )

    assert output.content == ""
    assert output.tool_calls == [
        ToolCall(id="call-1", name="analyze_image", arguments={"image_id": "img-1"})
    ]


def _response_with_arguments(
    family: str, arguments: object
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    response, events = _tool_only_response(family)
    function = (
        response["output"][0]
        if family == "openresponses"
        else response["choices"][0]["message"]["tool_calls"][0]["function"]
    )
    if arguments is Ellipsis:
        del function["arguments"]
    else:
        function["arguments"] = arguments
    return response, events


async def _tool_events(events: list[dict[str, Any]]) -> AsyncIterator[dict[str, Any]]:
    for event in events:
        yield event


@pytest.mark.parametrize("family", ["chatcompletions", "openresponses"])
@pytest.mark.parametrize("streaming", [False, True], ids=["unary", "stream"])
@pytest.mark.parametrize("arguments", ['{"first_frame":', "", "   ", "[]", "null"])
async def test_malformed_tool_arguments_never_become_default_inputs(
    family: str, streaming: bool, arguments: str
) -> None:
    client = create_client(
        modality="text", protocol=family, model="tool-turn", auth=NoAuth()
    )
    response, events = _response_with_arguments(family, arguments)
    tools = [_tool(NullableParams)]
    stream = (
        client._stream_class()(_tool_events(events), tools=tools) if streaming else None
    )

    with pytest.raises(ValidationError, match="analyze_image") as error:
        if stream is not None:
            _ = [chunk async for chunk in stream]
        else:
            validate_tool_calls(client._parse_tool_calls(response), tools)

    if arguments not in {"[]", "null"}:
        assert isinstance(error.value.__cause__, json.JSONDecodeError)
    if stream is not None:
        with pytest.raises(StopAsyncIteration):
            await anext(stream)
        with pytest.raises(StreamNotExhaustedError):
            _ = stream.output


@pytest.mark.parametrize("family", ["chatcompletions", "openresponses"])
@pytest.mark.parametrize(
    "arguments", [None, Ellipsis, []], ids=["null", "missing", "array"]
)
def test_completed_tool_arguments_require_an_object(
    family: str, arguments: object
) -> None:
    client = create_client(
        modality="text", protocol=family, model="tool-turn", auth=NoAuth()
    )
    response, _ = _response_with_arguments(family, arguments)
    with pytest.raises(ValidationError, match=r"analyze_image.*JSON object"):
        client._parse_tool_calls(response)


@pytest.mark.parametrize("family", ["chatcompletions", "openresponses"])
@pytest.mark.parametrize("arguments", ["{}", '{"first_frame":null}'])
async def test_valid_tool_arguments_survive_unary_and_fragmented_streams(
    family: str, arguments: str
) -> None:
    client = create_client(
        modality="text", protocol=family, model="tool-turn", auth=NoAuth()
    )
    response, events = _response_with_arguments(family, arguments)
    tools = [_tool(NullableParams)]
    expected = [
        ToolCall(id="call-1", name="analyze_image", arguments=json.loads(arguments))
    ]
    assert validate_tool_calls(client._parse_tool_calls(response), tools) == expected
    if family == "chatcompletions":
        midpoint = len(arguments) // 2
        call = events[0]["choices"][0]["delta"]["tool_calls"][0]
        call["function"] = {**call["function"], "arguments": arguments[:midpoint]}
        events.insert(
            1,
            {
                "object": "chat.completion.chunk",
                "choices": [
                    {
                        "delta": {
                            "tool_calls": [
                                {
                                    "index": 0,
                                    "function": {"arguments": arguments[midpoint:]},
                                }
                            ]
                        }
                    }
                ],
            },
        )
    stream = client._stream_class()(_tool_events(events), tools=tools)
    _ = [chunk async for chunk in stream]
    assert stream.output.tool_calls == expected
    response, _ = _response_with_arguments(family, json.loads(arguments))
    assert client._parse_tool_calls(response) == expected


async def test_truncated_chat_completion_arguments_fail_at_stream_end() -> None:
    client = create_client(
        modality="text", protocol="chatcompletions", model="tool-turn", auth=NoAuth()
    )
    _, events = _response_with_arguments("chatcompletions", '{"first_frame":')
    events[-1]["choices"][0]["finish_reason"] = "length"
    stream = client._stream_class()(_tool_events(events), tools=[_tool(NullableParams)])
    with pytest.raises(ValidationError, match="analyze_image"):
        _ = [chunk async for chunk in stream]
    with pytest.raises(StreamNotExhaustedError):
        _ = stream.output


@pytest.mark.parametrize("status", ["incomplete", "in_progress"])
async def test_unfinished_responses_arguments_remain_unexecutable(status: str) -> None:
    client = create_client(
        modality="text", protocol="openresponses", model="tool-turn", auth=NoAuth()
    )
    response, events = _response_with_arguments("openresponses", '{"first_frame":')
    response["output"][0]["status"] = status
    assert client._parse_tool_calls(response) == []
    stream = client._stream_class()(_tool_events(events))
    _ = [chunk async for chunk in stream]
    assert stream.output.tool_calls == []
    live = object.__new__(OpenAILiveStream)
    assert (
        live._parse_chunk_tool_calls(
            {
                "type": "response.event",
                "event": {
                    "type": "response.output_item.done",
                    "item": response["output"][0],
                },
            }
        )
        == []
    )


def test_live_delegation_rejects_malformed_completed_arguments() -> None:
    response, _ = _response_with_arguments("openresponses", '{"first_frame":')
    live = object.__new__(OpenAILiveStream)
    with pytest.raises(ValidationError, match="analyze_image") as error:
        live._parse_chunk_tool_calls(
            {
                "type": "response.event",
                "event": {
                    "type": "response.output_item.done",
                    "item": response["output"][0],
                },
            }
        )
    assert isinstance(error.value.__cause__, json.JSONDecodeError)
