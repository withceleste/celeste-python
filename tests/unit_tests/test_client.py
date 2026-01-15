"""High-value tests for ModalityClient - focusing on request building and framework behavior."""

from collections.abc import AsyncIterator
from enum import StrEnum
from typing import Any, Unpack

import pytest
from pydantic import SecretStr

from celeste.auth import APIKey
from celeste.client import ModalityClient
from celeste.core import Modality, Provider
from celeste.exceptions import StreamingNotSupportedError
from celeste.io import Chunk, Input, Output, Usage
from celeste.models import Model, Operation
from celeste.parameters import ParameterMapper, Parameters
from celeste.streaming import Stream
from celeste.types import TextContent


class ParamEnum(StrEnum):
    """Test parameter enum for unit tests."""

    TEST_PARAM = "test_param"
    FIRST_PARAM = "first_param"
    SECOND_PARAM = "second_param"


class _TestInput(Input):
    """Test input with prompt."""

    prompt: str


def _create_test_mapper(
    param_name: StrEnum,
    map_key: str | None = None,
) -> ParameterMapper:
    """Create a test parameter mapper instance."""
    actual_map_key = map_key if map_key is not None else param_name.value

    class TestMapperClass(ParameterMapper):
        """Test mapper implementation."""

        name: StrEnum = param_name

        def map(
            self,
            request: dict[str, Any],
            value: Any,  # noqa: ANN401
            model: Model,
        ) -> dict[str, Any]:
            if value is not None:
                request[actual_map_key] = value
            return request

        def parse_output(
            self, content: TextContent, value: object | None
        ) -> TextContent:
            return content

    return TestMapperClass()


def _create_transform_mapper(
    param_name: StrEnum,
    map_key: str | None = None,
) -> ParameterMapper:
    """Create a test parameter mapper that transforms output."""
    actual_map_key = map_key if map_key is not None else param_name.value

    class TransformMapperClass(ParameterMapper):
        """Test mapper with output transformation."""

        name: StrEnum = param_name

        def map(
            self,
            request: dict[str, Any],
            value: Any,  # noqa: ANN401
            model: Model,
        ) -> dict[str, Any]:
            if value is not None:
                request[actual_map_key] = value
            return request

        def parse_output(
            self, content: TextContent, value: object | None
        ) -> TextContent:
            if value is not None:
                return f"{content}_transformed_with_{value}"
            return content

    return TransformMapperClass()


@pytest.fixture
def text_model() -> Model:
    """Model that supports text generation."""
    return Model(
        id="gpt-4",
        provider=Provider.OPENAI,
        operations={Modality.TEXT: {Operation.GENERATE}},
        display_name="GPT-4",
    )


@pytest.fixture
def api_key() -> str:
    """Test API key."""
    return "sk-test123456789"


class ConcreteModalityClient(ModalityClient[_TestInput, Output, Parameters, str]):
    """Concrete ModalityClient implementation for testing."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return []

    def _init_request(self, inputs: _TestInput) -> dict[str, Any]:
        return {"prompt": inputs.prompt, "model": self.model.id}

    def _parse_usage(self, response_data: dict[str, Any]) -> Usage:
        return Usage()

    def _parse_content(  # type: ignore[override]
        self, response_data: dict[str, Any], **parameters: Unpack[Parameters]
    ) -> str:
        content = response_data.get("content", "test content")
        return content if isinstance(content, str) else "test content"

    @classmethod
    def _output_class(cls) -> type[Output]:
        return Output

    async def _make_request(  # type: ignore[override]
        self,
        request_body: dict[str, Any],
        *,
        endpoint: str | None = None,
        **parameters: Unpack[Parameters],
    ) -> dict[str, Any]:
        return {"content": "test content"}

    def _stream_class(self) -> type[Stream[Output, Parameters, Chunk]]:
        raise NotImplementedError("Streaming not implemented in test client")

    def _make_stream_request(  # type: ignore[override]
        self, request_body: dict[str, Any], **parameters: Unpack[Parameters]
    ) -> AsyncIterator[dict[str, Any]]:
        raise NotImplementedError("Streaming not implemented in test client")


class TestModalityClientRequestBuilding:
    """Test ModalityClient._build_request parameter mapping logic."""

    @pytest.mark.smoke
    def test_build_request_applies_parameter_mappers_correctly(
        self, text_model: Model, api_key: str
    ) -> None:
        """_build_request applies all parameter mappers in sequence."""

        # Arrange
        class ClientWithMapper(ConcreteModalityClient):
            """Client with custom parameter mapper."""

            @classmethod
            def parameter_mappers(cls) -> list[ParameterMapper]:
                return [_create_test_mapper(ParamEnum.TEST_PARAM)]

        client = ClientWithMapper(
            modality=Modality.TEXT,
            model=text_model,
            provider=text_model.provider,
            auth=APIKey(secret=SecretStr(api_key)),
        )

        inputs = _TestInput(prompt="test prompt")

        # Act
        request = client._build_request(inputs, test_param="mapped_value")

        # Assert
        assert request["prompt"] == "test prompt"
        assert request["test_param"] == "mapped_value"

    def test_build_request_with_multiple_mappers(
        self, text_model: Model, api_key: str
    ) -> None:
        """_build_request applies multiple parameter mappers in order."""

        # Arrange
        class ClientWithMultipleMappers(ConcreteModalityClient):
            """Client with multiple parameter mappers."""

            @classmethod
            def parameter_mappers(cls) -> list[ParameterMapper]:
                return [
                    _create_test_mapper(ParamEnum.FIRST_PARAM),
                    _create_test_mapper(ParamEnum.SECOND_PARAM),
                ]

        client = ClientWithMultipleMappers(
            modality=Modality.TEXT,
            model=text_model,
            provider=text_model.provider,
            auth=APIKey(secret=SecretStr(api_key)),
        )

        inputs = _TestInput(prompt="test prompt")

        # Act
        request = client._build_request(
            inputs, first_param="first", second_param="second"
        )

        # Assert
        assert request["first_param"] == "first"
        assert request["second_param"] == "second"

    @pytest.mark.parametrize(
        "param_value,expected_output",
        [
            ("test_value", "original content_transformed_with_test_value"),
            (None, "original content"),
        ],
        ids=["with_value", "with_none"],
    )
    def test_transform_output_applies_mappers(
        self,
        text_model: Model,
        api_key: str,
        param_value: str | None,
        expected_output: str,
    ) -> None:
        """_transform_output applies parameter mapper output transformations."""

        # Arrange
        class ClientWithTransformMapper(ConcreteModalityClient):
            """Client with output transformation mapper."""

            @classmethod
            def parameter_mappers(cls) -> list[ParameterMapper]:
                return [_create_transform_mapper(ParamEnum.TEST_PARAM)]

        client = ClientWithTransformMapper(
            modality=Modality.TEXT,
            model=text_model,
            provider=text_model.provider,
            auth=APIKey(secret=SecretStr(api_key)),
        )

        original_content = "original content"

        # Act
        kwargs = {"test_param": param_value} if param_value is not None else {}
        transformed = client._transform_output(original_content, **kwargs)

        # Assert
        assert transformed == expected_output


class TestModalityClientStreaming:
    """Test ModalityClient._stream default behavior."""

    def test_stream_raises_not_supported_for_non_streaming_model(
        self, api_key: str
    ) -> None:
        """_stream raises StreamingNotSupportedError when model doesn't support streaming."""
        # Arrange
        non_streaming_model = Model(
            id="non-streaming-model",
            provider=Provider.OPENAI,
            operations={Modality.TEXT: {Operation.GENERATE}},
            display_name="Non-Streaming Model",
            streaming=False,  # Streaming disabled
        )

        client = ConcreteModalityClient(
            modality=Modality.TEXT,
            model=non_streaming_model,
            provider=non_streaming_model.provider,
            auth=APIKey(secret=SecretStr(api_key)),
        )

        # Act & Assert
        with pytest.raises(StreamingNotSupportedError) as exc_info:
            client._stream(
                _TestInput(prompt="test"),
                stream_class=Stream,  # type: ignore
            )

        # Verify error message
        error_msg = str(exc_info.value)
        assert "Streaming not supported" in error_msg
        assert "non-streaming-model" in error_msg
