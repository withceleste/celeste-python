import warnings
from enum import StrEnum
from typing import Any, ClassVar, Unpack
from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from celeste.auth import NoAuth
from celeste.client import ModalityClient
from celeste.core import Modality, Operation, Provider
from celeste.exceptions import StreamingNotSupportedError, UnsupportedParameterWarning
from celeste.io import Chunk, Input, Output, Usage
from celeste.modalities.text.client import TextSyncNamespace
from celeste.modalities.text.io import TextOutput
from celeste.models import Model
from celeste.parameters import FieldMapper, ParameterMapper, Parameters


class FakeParameter(StrEnum):
    VALUE = "value"
    TRANSFORM = "transform"


class ValueMapper(FieldMapper[str]):
    name = FakeParameter.VALUE
    field = "mapped"


class TransformMapper(ParameterMapper[str]):
    name = FakeParameter.TRANSFORM

    def map(
        self,
        request: dict[str, Any],
        value: Any,  # noqa: ANN401
        model: Model,
    ) -> dict[str, Any]:
        return request

    def parse_output(self, content: str, value: object | None) -> str:
        return f"{content}:{value}" if value is not None else content


class FakeInput(Input):
    prompt: str


class FakeClient(ModalityClient[FakeInput, Output, Parameters, str, Chunk]):
    mappers: ClassVar[list[ParameterMapper[str]]] = [ValueMapper(), TransformMapper()]

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[str]]:
        return cls.mappers

    def _init_request(self, inputs: FakeInput) -> dict[str, Any]:
        return {"prompt": inputs.prompt}

    def _parse_usage(self, response_data: dict[str, Any]) -> dict[str, int]:
        return response_data.get("usage", {})

    def _parse_content(self, response_data: dict[str, Any]) -> str:
        return str(response_data["content"])

    @classmethod
    def _output_class(cls) -> type[Output]:
        return Output

    async def _make_request(
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[Parameters],
    ) -> dict[str, Any]:
        return {
            "content": request_body.get("mapped", "raw"),
            "usage": {},
            "model": "resolved-model",
        }


@pytest.fixture
def model() -> Model:
    return Model(
        id="test-model",
        provider=Provider.OPENAI,
        display_name="Test Model",
        operations={Modality.TEXT: {Operation.GENERATE}},
    )


@pytest.fixture
def client(model: Model) -> FakeClient:
    return FakeClient(
        modality=Modality.TEXT,
        model=model,
        provider=model.provider,
        auth=NoAuth(),
    )


def test_build_request_applies_mappers(client: FakeClient) -> None:
    assert client._build_request(FakeInput(prompt="hello"), value="mapped") == {
        "prompt": "hello",
        "mapped": "mapped",
    }


def test_build_request_warns_only_for_non_none_unsupported_values(
    client: FakeClient,
) -> None:
    with pytest.warns(UnsupportedParameterWarning, match="unsupported.*test-model"):
        client._build_request(FakeInput(prompt="hello"), unsupported="value")

    with warnings.catch_warnings():
        warnings.simplefilter("error", UnsupportedParameterWarning)
        client._build_request(FakeInput(prompt="hello"), unsupported=None)


async def test_predict_maps_request_and_transforms_output(client: FakeClient) -> None:
    output = await client._predict(
        FakeInput(prompt="hello"), value="mapped", transform="normalized"
    )
    assert output.content == "mapped:normalized"
    assert isinstance(output.usage, Usage)
    assert output.metadata["response_model"] == "resolved-model"


@pytest.mark.parametrize(
    "content", [b"\xff binary", b"\xff\xfe\x00\x00", b"\x80\x81\x82"]
)
def test_binary_error_body_raises_http_error(
    client: FakeClient, content: bytes
) -> None:
    response = httpx.Response(
        500,
        content=content,
        request=httpx.Request("POST", "https://example.com"),
    )
    with pytest.raises(httpx.HTTPStatusError):
        client._handle_error_response(response)


def test_non_streaming_model_is_rejected(model: Model) -> None:
    model.streaming = False
    client = FakeClient(
        modality=Modality.TEXT,
        model=model,
        provider=model.provider,
        auth=NoAuth(),
    )
    with pytest.raises(StreamingNotSupportedError, match="test-model"):
        client._stream(FakeInput(prompt="hello"), stream_class=object)  # type: ignore[arg-type]


def test_sync_namespace_delegates_to_async_prediction() -> None:
    expected = TextOutput(content="hello")
    client = Mock()
    client._predict = AsyncMock(return_value=expected)

    result = TextSyncNamespace(client).generate("hello", temperature=0.2)

    assert result is expected
    client._check_media_support.assert_called_once_with(messages=None)
    inputs = client._predict.await_args.args[0]
    assert inputs.prompt == "hello"
    assert client._predict.await_args.kwargs["temperature"] == 0.2
