"""Tests for custom exception classes."""

import pytest

from celeste.exceptions import (
    CelesteError,
    ClientNotFoundError,
    ConstraintViolationError,
    MissingCredentialsError,
    ModelNotFoundError,
    StreamEmptyError,
    StreamingNotSupportedError,
    StreamNotExhaustedError,
    UnsupportedCapabilityError,
    UnsupportedParameterError,
)


class TestExceptionHierarchy:
    """Test exception hierarchy and inheritance."""

    def test_all_exceptions_inherit_from_celeste_error(self) -> None:
        """Test that all custom exceptions inherit from CelesteError."""
        exceptions = [
            ModelNotFoundError("model-1", "openai"),
            UnsupportedCapabilityError("model-1", "text_generation"),
            ClientNotFoundError("text_generation", "openai"),
            StreamingNotSupportedError("model-1"),
            StreamNotExhaustedError(),
            StreamEmptyError(),
            MissingCredentialsError("openai"),
            UnsupportedParameterError("temperature", "model-1"),
        ]

        for exc in exceptions:
            assert isinstance(exc, CelesteError)
            assert isinstance(exc, Exception)


class TestModelNotFoundError:
    """Test ModelNotFoundError exception."""

    def test_creates_with_model_and_provider(self) -> None:
        """Test exception stores model and provider attributes."""
        exc = ModelNotFoundError("gpt-4", "openai")

        assert exc.model_id == "gpt-4"
        assert exc.provider == "openai"
        assert "gpt-4" in str(exc)
        assert "openai" in str(exc)

    def test_message_is_descriptive(self) -> None:
        """Test exception message is clear and actionable."""
        exc = ModelNotFoundError("claude-3", "anthropic")

        assert str(exc) == "Model 'claude-3' not found for provider anthropic"


class TestUnsupportedCapabilityError:
    """Test UnsupportedCapabilityError exception."""

    def test_creates_with_model_and_capability(self) -> None:
        """Test exception stores model and capability attributes."""
        exc = UnsupportedCapabilityError("gpt-4", "image_generation")

        assert exc.model_id == "gpt-4"
        assert exc.capability == "image_generation"
        assert "gpt-4" in str(exc)
        assert "image_generation" in str(exc)

    def test_message_is_descriptive(self) -> None:
        """Test exception message is clear and actionable."""
        exc = UnsupportedCapabilityError("gpt-3.5-turbo", "video_generation")

        assert (
            str(exc)
            == "Model 'gpt-3.5-turbo' does not support capability 'video_generation'"
        )


class TestClientNotFoundError:
    """Test ClientNotFoundError exception."""

    def test_creates_with_capability_and_provider(self) -> None:
        """Test exception stores capability and provider attributes."""
        exc = ClientNotFoundError("text_generation", "unknown_provider")

        assert exc.capability == "text_generation"
        assert exc.provider == "unknown_provider"
        assert "text_generation" in str(exc)
        assert "unknown_provider" in str(exc)


class TestStreamingNotSupportedError:
    """Test StreamingNotSupportedError exception."""

    def test_creates_with_model_id(self) -> None:
        """Test exception stores model_id attribute."""
        exc = StreamingNotSupportedError("dall-e-3")

        assert exc.model_id == "dall-e-3"
        assert "dall-e-3" in str(exc)
        assert "Streaming not supported" in str(exc)


class TestStreamNotExhaustedError:
    """Test StreamNotExhaustedError exception."""

    def test_has_helpful_message(self) -> None:
        """Test exception message guides user to consume chunks first."""
        exc = StreamNotExhaustedError()

        message = str(exc)
        assert "not exhausted" in message.lower()
        assert "consume all chunks" in message.lower()
        assert ".output" in message


class TestStreamEmptyError:
    """Test StreamEmptyError exception."""

    def test_has_descriptive_message(self) -> None:
        """Test exception message describes the problem clearly."""
        exc = StreamEmptyError()

        message = str(exc)
        assert "completed" in message.lower()
        assert "no chunks" in message.lower()


class TestMissingCredentialsError:
    """Test MissingCredentialsError exception."""

    def test_creates_with_provider(self) -> None:
        """Test exception stores provider attribute."""
        exc = MissingCredentialsError("openai")

        assert exc.provider == "openai"
        assert "openai" in str(exc)

    def test_message_provides_guidance(self) -> None:
        """Test exception message helps user resolve the issue."""
        exc = MissingCredentialsError("anthropic")

        message = str(exc)
        assert "anthropic" in message
        assert "environment variable" in message.lower()
        assert "api_key" in message.lower()


class TestUnsupportedParameterError:
    """Test UnsupportedParameterError exception."""

    def test_creates_with_parameter_and_model(self) -> None:
        """Test exception stores parameter and model_id attributes."""
        exc = UnsupportedParameterError("temperature", "dall-e-3")

        assert exc.parameter == "temperature"
        assert exc.model_id == "dall-e-3"
        assert "temperature" in str(exc)
        assert "dall-e-3" in str(exc)

    def test_message_is_clear(self) -> None:
        """Test exception message clearly indicates the problem."""
        exc = UnsupportedParameterError("max_tokens", "whisper-1")

        assert (
            str(exc) == "Parameter 'max_tokens' is not supported by model 'whisper-1'"
        )


class TestExceptionUsability:
    """Test that exceptions can be raised and caught properly."""

    def test_can_catch_specific_exception(self) -> None:
        """Test specific exception types can be caught."""
        with pytest.raises(ModelNotFoundError) as exc_info:
            raise ModelNotFoundError("test-model", "test-provider")

        assert exc_info.value.model_id == "test-model"

    def test_can_catch_base_exception(self) -> None:
        """Test all custom exceptions can be caught as CelesteError."""
        with pytest.raises(CelesteError):
            raise StreamEmptyError()

    def test_can_access_exception_attributes(self) -> None:
        """Test exception attributes are accessible after catching."""
        try:
            raise UnsupportedParameterError("seed", "gpt-4")
        except UnsupportedParameterError as e:
            assert e.parameter == "seed"
            assert e.model_id == "gpt-4"
