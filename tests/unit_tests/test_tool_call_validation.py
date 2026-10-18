"""Tool-call arguments are validated at the response boundary."""

from collections.abc import AsyncIterator
from enum import StrEnum
from typing import Any

import pytest
from pydantic import BaseModel

from celeste.exceptions import ValidationError
from celeste.io import Chunk, Output
from celeste.parameters import Parameters
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
