"""Tool-call argument validation tests."""

from collections.abc import AsyncIterator
from enum import StrEnum
from typing import Any, Unpack

import pytest
from pydantic import BaseModel, SecretStr

from celeste.auth import APIKey
from celeste.client import ModalityClient
from celeste.core import Modality, Provider
from celeste.exceptions import ValidationError
from celeste.io import Chunk, Input, Output
from celeste.modalities.text.parameters import TextParameter
from celeste.models import Model, Operation
from celeste.parameters import ParameterMapper, Parameters
from celeste.streaming import Stream
from celeste.tools import CodeExecution, ToolCall, validate_tool_calls


class ImageId(StrEnum):
    IMG_1 = "img-1"


class AnalyzeImageParams(BaseModel):
    image_id: ImageId


class NoFirstFrameParams(BaseModel):
    first_frame: None = None


def _tool(parameters: type[BaseModel]) -> dict[str, object]:
    return {"name": "analyze_image", "parameters": parameters}


def _model() -> Model:
    return Model(
        id="test-model",
        provider=Provider.OPENAI,
        display_name="Test Model",
        operations={Modality.TEXT: {Operation.GENERATE}},
    )


class _TextInput(Input):
    prompt: str


class _ToolsMapper(ParameterMapper[str]):
    name = TextParameter.TOOLS

    def map(
        self,
        request: dict[str, Any],
        value: Any,  # noqa: ANN401
        model: Model,
    ) -> dict[str, Any]:
        return request


class _Client(ModalityClient[_TextInput, Output[str], Parameters, str, Chunk[str]]):
    returned_tool_calls: list[ToolCall]

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[str]]:
        return [_ToolsMapper()]

    def _init_request(self, inputs: _TextInput) -> dict[str, Any]:
        return {"prompt": inputs.prompt}

    def _parse_usage(
        self, response_data: dict[str, Any]
    ) -> dict[str, int | float | None]:
        return {}

    def _parse_content(self, response_data: dict[str, Any]) -> str:
        return "ok"

    @classmethod
    def _output_class(cls) -> type[Output[str]]:
        return Output[str]

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[Parameters],
    ) -> dict[str, Any]:
        return {}

    def _parse_tool_calls(self, response_data: dict[str, Any]) -> list[ToolCall]:
        return self.returned_tool_calls


class _Stream(Stream[Output[str], Parameters, Chunk[str]]):
    _chunk_class = Chunk[str]
    _output_class = Output[str]
    _empty_content = ""
    returned_tool_calls: list[ToolCall]

    def _aggregate_content(self, chunks: list[Chunk[str]]) -> str:
        return "".join(chunk.content for chunk in chunks)

    def _aggregate_tool_calls(
        self,
        chunks: list[Chunk[str]],
        raw_events: list[dict[str, Any]],
    ) -> list[ToolCall]:
        return self.returned_tool_calls


async def _empty_events() -> AsyncIterator[dict[str, Any]]:
    if False:
        yield {}


def test_validate_tool_calls_accepts_enum_and_preserves_extra_fields() -> None:
    call = ToolCall(
        id="call-1",
        name="analyze_image",
        arguments={"image_id": "img-1"},
        thoughtSignature="sig-1",
    )

    validated = validate_tool_calls([call], [_tool(AnalyzeImageParams)])

    assert validated[0].arguments == {"image_id": "img-1"}
    assert validated[0].thoughtSignature == "sig-1"


def test_validate_tool_calls_rejects_invalid_enum_argument() -> None:
    call = ToolCall(id="call-1", name="analyze_image", arguments={"image_id": "fake"})

    with pytest.raises(ValidationError, match=r"fake"):
        validate_tool_calls([call], [_tool(AnalyzeImageParams)])


@pytest.mark.parametrize("arguments", [{}, {"first_frame": None}])
def test_validate_tool_calls_allows_omitted_or_null_null_only_argument(
    arguments: dict[str, object],
) -> None:
    call = ToolCall(id="call-1", name="analyze_image", arguments=arguments)

    validated = validate_tool_calls([call], [_tool(NoFirstFrameParams)])

    assert validated[0].arguments == arguments


def test_validate_tool_calls_rejects_string_for_null_only_argument() -> None:
    call = ToolCall(
        id="call-1",
        name="analyze_image",
        arguments={"first_frame": "img-1"},
    )

    with pytest.raises(ValidationError, match="first_frame"):
        validate_tool_calls([call], [_tool(NoFirstFrameParams)])


def test_validate_tool_calls_ignores_raw_schema_and_builtin_tools() -> None:
    call = ToolCall(id="call-1", name="raw_tool", arguments={"anything": "ok"})

    assert validate_tool_calls(
        [call],
        [{"name": "raw_tool", "parameters": {"type": "object"}}, CodeExecution()],
    ) == [call]


async def test_predict_rejects_invalid_returned_tool_call() -> None:
    client = _Client(
        modality=Modality.TEXT,
        model=_model(),
        provider=Provider.OPENAI,
        auth=APIKey(secret=SecretStr("test")),
        returned_tool_calls=[
            ToolCall(id="call-1", name="analyze_image", arguments={"image_id": "fake"})
        ],
    )

    with pytest.raises(ValidationError, match="fake"):
        await client._predict(
            _TextInput(prompt="test"), tools=[_tool(AnalyzeImageParams)]
        )


def test_stream_output_rejects_invalid_returned_tool_call() -> None:
    stream = _Stream(_empty_events(), tools=[_tool(AnalyzeImageParams)])
    stream.returned_tool_calls = [
        ToolCall(id="call-1", name="analyze_image", arguments={"image_id": "fake"})
    ]

    with pytest.raises(ValidationError, match="fake"):
        stream._parse_output(
            [Chunk[str](content="ok")], tools=[_tool(AnalyzeImageParams)]
        )
