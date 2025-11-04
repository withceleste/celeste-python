"""High-value tests for Client - focusing on critical validation and framework behavior."""

from collections.abc import Generator
from enum import StrEnum
from typing import Any, Unpack

import pytest
from pydantic import SecretStr, ValidationError

from celeste.client import Client, _clients, get_client_class, register_client
from celeste.core import Capability, Provider
from celeste.io import Input, Output, Usage
from celeste.models import Model
from celeste.parameters import ParameterMapper, Parameters


class ParamEnum(StrEnum):
    """Test parameter enum for unit tests."""

    TEST_PARAM = "test_param"
    FIRST_PARAM = "first_param"
    SECOND_PARAM = "second_param"


class _TestInput(Input):
    """Test input with prompt."""

    prompt: str


def _create_test_client_class(
    generate_output: str = "test output",
    class_name: str | None = None,
) -> type[Client]:
    """Create a test client class with minimal implementation."""
    if class_name is None:
        class_name = f"TestClient_{generate_output.replace(' ', '_')}"

    class TestClientClass(Client):
        """Test client implementation."""

        @classmethod
        def parameter_mappers(cls) -> list[ParameterMapper]:
            return []

        def _init_request(self, inputs: Input) -> dict[str, Any]:
            prompt = getattr(inputs, "prompt", "test prompt")
            return {"prompt": prompt}

        def _parse_usage(self, response_data: dict[str, Any]) -> Usage:
            return Usage()

        def _parse_content(
            self, response_data: dict[str, Any], **parameters: Unpack[Parameters]
        ) -> Any:  # noqa: ANN401
            return response_data.get("content", "test content")

        async def generate(self, **parameters: Unpack[Parameters]) -> Output:
            return Output(content=generate_output)

    TestClientClass.__name__ = class_name
    return TestClientClass


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

        def parse_output(self, content: object, value: object | None) -> object:
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

        def parse_output(self, content: object, value: object | None) -> object:
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
        capabilities={Capability.TEXT_GENERATION},
        display_name="GPT-4",
    )


@pytest.fixture
def multimodal_model() -> Model:
    """Model that supports both text and image capabilities."""
    return Model(
        id="gpt-4-vision",
        provider=Provider.OPENAI,
        capabilities={Capability.TEXT_GENERATION, Capability.IMAGE_GENERATION},
        display_name="GPT-4 Vision",
    )


@pytest.fixture
def api_key() -> str:
    """Test API key."""
    return "sk-test123456789"


class ConcreteClient(Client):
    """Concrete implementation for testing Client behavior."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return []

    def _init_request(self, inputs: Input) -> dict[str, Any]:
        prompt = getattr(inputs, "prompt", "test prompt")
        return {"prompt": prompt, "model": self.model.id}

    def _parse_usage(self, response_data: dict[str, Any]) -> Usage:
        return Usage()

    def _parse_content(
        self, response_data: dict[str, Any], **parameters: Unpack[Parameters]
    ) -> Any:  # noqa: ANN401
        return response_data.get("content", "test content")

    async def generate(self, **parameters: Unpack[Parameters]) -> Output:
        return Output(content="test output")


class TestClientValidation:
    """Test Client critical validation behaviors."""

    @pytest.mark.smoke
    def test_successful_creation_with_compatible_capability(
        self, text_model: Model, api_key: str
    ) -> None:
        """Client accepts model that supports the required capability."""
        # Arrange & Act
        client = ConcreteClient(
            model=text_model,
            provider=text_model.provider,
            capability=Capability.TEXT_GENERATION,
            api_key=SecretStr(api_key),
        )

        # Assert
        assert client.model == text_model
        assert client.capability == Capability.TEXT_GENERATION

    def test_validation_failure_with_incompatible_capability(
        self, text_model: Model, api_key: str
    ) -> None:
        """Client rejects model that lacks required capability."""
        # Arrange & Act & Assert
        with pytest.raises(
            ValidationError,
            match=r"Model 'gpt-4' does not support capability image_generation",
        ):
            ConcreteClient(
                model=text_model,
                provider=text_model.provider,
                capability=Capability.IMAGE_GENERATION,  # Model doesn't support this
                api_key=SecretStr(api_key),
            )

    @pytest.mark.parametrize(
        "capability,description",
        [
            (Capability.TEXT_GENERATION, "text capability from multimodal model"),
            (Capability.IMAGE_GENERATION, "image capability from multimodal model"),
        ],
        ids=["text_capability", "image_capability"],
    )
    def test_validation_success_with_supported_capabilities(
        self,
        multimodal_model: Model,
        api_key: str,
        capability: Capability,
        description: str,
    ) -> None:
        """Client accepts model that supports requested capability."""
        # Arrange & Act
        client = ConcreteClient(
            model=multimodal_model,
            provider=multimodal_model.provider,
            capability=capability,
            api_key=SecretStr(api_key),
        )

        # Assert
        assert client.model == multimodal_model
        assert client.capability == capability

    def test_validation_fails_with_model_lacking_any_capabilities(
        self, api_key: str
    ) -> None:
        """Client rejects models with empty capability set."""
        # Arrange
        empty_model = Model(
            id="broken-model",
            provider=Provider.OPENAI,
            capabilities=set(),  # No capabilities
            display_name="Broken Model",
        )

        # Act & Assert
        with pytest.raises(
            ValidationError,
            match=r"Model 'broken-model' does not support capability text_generation",
        ):
            ConcreteClient(
                model=empty_model,
                provider=empty_model.provider,
                capability=Capability.TEXT_GENERATION,
                api_key=SecretStr(api_key),
            )


class TestClientRegistry:
    """Test client registry functions - register_client and get_client_class."""

    @pytest.fixture(autouse=True)
    def clear_registry(self) -> Generator[None, None, None]:
        """Clear the client registry before each test to ensure isolation."""
        # Arrange - Store original state and clear registry
        original_clients = _clients.copy()
        _clients.clear()

        yield

        # Cleanup - Restore original state
        _clients.clear()
        _clients.update(original_clients)

    @pytest.mark.smoke
    def test_register_and_retrieve_client_success(self) -> None:
        """Registry stores and retrieves client classes correctly."""
        # Arrange
        capability = Capability.TEXT_GENERATION
        provider = Provider.OPENAI

        # Act
        register_client(capability, provider, ConcreteClient)
        retrieved_class = get_client_class(capability, provider)

        # Assert
        assert retrieved_class is ConcreteClient

    def test_get_client_class_raises_for_unregistered_capability(self) -> None:
        """get_client_class raises NotImplementedError for unregistered capabilities."""
        # Arrange
        unregistered_capability = Capability.IMAGE_GENERATION
        provider = Provider.OPENAI

        # Act & Assert
        with pytest.raises(
            NotImplementedError, match=r"No client registered for image_generation"
        ):
            get_client_class(unregistered_capability, provider)

    def test_register_client_overwrites_previous_registration(self) -> None:
        """Registering a new client for existing capability overwrites the previous one."""
        # Arrange
        capability = Capability.TEXT_GENERATION
        provider = Provider.OPENAI

        FirstClient = _create_test_client_class("first client", "FirstClient")
        SecondClient = _create_test_client_class("second client", "SecondClient")

        # Act
        register_client(capability, provider, FirstClient)
        register_client(capability, provider, SecondClient)  # Overwrite
        retrieved_class = get_client_class(capability, provider)

        # Assert
        assert retrieved_class is SecondClient

    def test_registry_isolation_between_different_capabilities(self) -> None:
        """Different capabilities stored independently in the registry."""
        # Arrange
        text_capability = Capability.TEXT_GENERATION
        image_capability = Capability.IMAGE_GENERATION
        provider = Provider.OPENAI

        TextClient = _create_test_client_class("text output", "TextClient")
        ImageClient = _create_test_client_class("image output", "ImageClient")

        # Act
        register_client(text_capability, provider, TextClient)
        register_client(image_capability, provider, ImageClient)

        # Assert
        assert get_client_class(text_capability, provider) is TextClient
        assert get_client_class(image_capability, provider) is ImageClient

    @pytest.mark.parametrize(
        "missing_capability,provider,expected_capability_str,expected_provider_str",
        [
            (
                Capability.IMAGE_GENERATION,
                Provider.ANTHROPIC,
                "image_generation",
                "anthropic",
            ),
            (
                Capability.VIDEO_GENERATION,
                Provider.OPENAI,
                "video_generation",
                "openai",
            ),
        ],
        ids=["image_anthropic", "video_openai"],
    )
    def test_exception_message_includes_capability_and_provider(
        self,
        missing_capability: Capability,
        provider: Provider,
        expected_capability_str: str,
        expected_provider_str: str,
    ) -> None:
        """NotImplementedError includes both capability and provider for debugging."""
        # Arrange & Act & Assert
        with pytest.raises(NotImplementedError) as exc_info:
            get_client_class(missing_capability, provider)

        # Assert both parts in error message
        error_msg = str(exc_info.value)
        assert expected_capability_str in error_msg
        assert expected_provider_str in error_msg


class TestClientRequestBuilding:
    """Test Client._build_request parameter mapping logic."""

    @pytest.mark.smoke
    def test_build_request_applies_parameter_mappers_correctly(
        self, text_model: Model, api_key: str
    ) -> None:
        """_build_request applies all parameter mappers in sequence."""

        # Arrange
        class ClientWithMapper(ConcreteClient):
            """Client with custom parameter mapper."""

            @classmethod
            def parameter_mappers(cls) -> list[ParameterMapper]:
                """Return test mapper."""
                return [_create_test_mapper(ParamEnum.TEST_PARAM)]

        client = ClientWithMapper(
            model=text_model,
            provider=text_model.provider,
            capability=Capability.TEXT_GENERATION,
            api_key=SecretStr(api_key),
        )

        inputs = _TestInput(prompt="test prompt")

        # Act
        request = client._build_request(inputs, test_param="mapped_value")  # type: ignore[call-arg]

        # Assert
        assert request["prompt"] == "test prompt"
        assert request["test_param"] == "mapped_value"

    def test_build_request_with_multiple_mappers(
        self, text_model: Model, api_key: str
    ) -> None:
        """_build_request applies multiple parameter mappers in order."""

        # Arrange
        class ClientWithMultipleMappers(ConcreteClient):
            """Client with multiple parameter mappers."""

            @classmethod
            def parameter_mappers(cls) -> list[ParameterMapper]:
                """Return multiple test mappers."""
                return [
                    _create_test_mapper(ParamEnum.FIRST_PARAM),
                    _create_test_mapper(ParamEnum.SECOND_PARAM),
                ]

        client = ClientWithMultipleMappers(
            model=text_model,
            provider=text_model.provider,
            capability=Capability.TEXT_GENERATION,
            api_key=SecretStr(api_key),
        )

        inputs = _TestInput(prompt="test prompt")

        # Act
        request = client._build_request(
            inputs, first_param="first", second_param="second"
        )  # type: ignore[call-arg]

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
        class ClientWithTransformMapper(ConcreteClient):
            """Client with output transformation mapper."""

            @classmethod
            def parameter_mappers(cls) -> list[ParameterMapper]:
                """Return transform mapper."""
                return [_create_transform_mapper(ParamEnum.TEST_PARAM)]

        client = ClientWithTransformMapper(
            model=text_model,
            provider=text_model.provider,
            capability=Capability.TEXT_GENERATION,
            api_key=SecretStr(api_key),
        )

        original_content = "original content"

        # Act
        kwargs = {"test_param": param_value} if param_value is not None else {}
        transformed = client._transform_output(original_content, **kwargs)

        # Assert
        assert transformed == expected_output


class TestClientStreaming:
    """Test Client.stream default behavior."""

    def test_stream_raises_not_implemented_with_descriptive_error(
        self, text_model: Model, api_key: str
    ) -> None:
        """stream() raises NotImplementedError with capability and provider info."""
        # Arrange
        client = ConcreteClient(
            model=text_model,
            provider=text_model.provider,
            capability=Capability.TEXT_GENERATION,
            api_key=SecretStr(api_key),
        )

        # Act & Assert
        with pytest.raises(NotImplementedError) as exc_info:
            client.stream()

        # Verify error message contains all debugging info
        error_msg = str(exc_info.value)
        assert "Streaming not supported" in error_msg
        assert "text_generation" in error_msg
        assert "openai" in error_msg
