"""Tests for protocol= + base_url= support."""

from unittest.mock import MagicMock

import pytest

from celeste import Protocol, create_client
from celeste.auth import AuthHeader, NoAuth
from celeste.exceptions import ModelNotFoundError
from celeste.modalities.text.protocols.chatcompletions.client import (
    ChatCompletionsTextClient,
)
from celeste.modalities.text.protocols.openresponses.client import (
    OpenResponsesTextClient,
)
from celeste.protocols.chatcompletions.client import ChatCompletionsClient
from celeste.protocols.openresponses.client import OpenResponsesClient


class TestCreateClientWithProtocol:
    """Test create_client with protocol= parameter."""

    def test_protocol_openresponses_returns_correct_client(self) -> None:
        client = create_client(
            protocol="openresponses",
            base_url="http://localhost:11434",
            model="test-model",
            modality="text",
            operation="generate",
        )
        assert isinstance(client, OpenResponsesTextClient)

    def test_protocol_chatcompletions_returns_correct_client(self) -> None:
        client = create_client(
            protocol="chatcompletions",
            base_url="https://api.example.com",
            model="test-model",
            modality="text",
            operation="generate",
            api_key="test-key",
        )
        assert isinstance(client, ChatCompletionsTextClient)

    def test_protocol_sets_base_url_on_client(self) -> None:
        client = create_client(
            protocol="openresponses",
            base_url="http://localhost:11434",
            model="test-model",
            modality="text",
            operation="generate",
        )
        assert client.base_url == "http://localhost:11434"

    def test_protocol_client_has_protocol_and_no_provider(self) -> None:
        client = create_client(
            protocol="openresponses",
            base_url="http://localhost:11434",
            model="test-model",
            modality="text",
            operation="generate",
        )
        assert client.protocol == Protocol.OPENRESPONSES
        assert client.provider is None

    def test_protocol_enum_value_accepted(self) -> None:
        client = create_client(
            protocol=Protocol.CHATCOMPLETIONS,
            base_url="https://api.example.com",
            model="test-model",
            modality="text",
            operation="generate",
            api_key="test-key",
        )
        assert isinstance(client, ChatCompletionsTextClient)


class TestCreateClientWithBaseUrl:
    """Test create_client with base_url= parameter."""

    def test_base_url_without_protocol_defaults_to_openresponses(self) -> None:
        client = create_client(
            base_url="http://localhost:11434",
            model="test-model",
            modality="text",
            operation="generate",
        )
        assert isinstance(client, OpenResponsesTextClient)
        assert client.base_url == "http://localhost:11434"

    def test_base_url_with_provider_sets_base_url(self) -> None:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            client = create_client(
                provider="openai",
                base_url="https://my-proxy.com",
                model="custom-model",
                modality="text",
                operation="generate",
                api_key="test-key",
            )
        assert client.base_url == "https://my-proxy.com"

    def test_no_base_url_no_protocol_no_provider_raises(self) -> None:
        with pytest.raises(ModelNotFoundError):
            create_client(
                model="unknown-model",
                modality="text",
                operation="generate",
            )


class TestProtocolAuth:
    """Test auth resolution for protocol path."""

    def test_protocol_no_auth_no_key_defaults_to_noauth(self) -> None:
        client = create_client(
            protocol="openresponses",
            base_url="http://localhost:11434",
            model="test-model",
            modality="text",
            operation="generate",
        )
        assert isinstance(client.auth, NoAuth)

    def test_protocol_with_api_key_uses_authheader(self) -> None:
        client = create_client(
            protocol="chatcompletions",
            base_url="https://api.example.com",
            model="test-model",
            modality="text",
            operation="generate",
            api_key="my-secret-key",
        )
        assert isinstance(client.auth, AuthHeader)


class TestBuildUrlWithBaseUrl:
    """Test _build_url uses instance base_url when set."""

    def test_openresponses_build_url_uses_base_url(self) -> None:
        client = MagicMock(spec=OpenResponsesClient)
        client.base_url = "https://custom.example.com"
        client._default_base_url = "https://api.openai.com"
        client._build_url = OpenResponsesClient._build_url.__get__(client)

        url = client._build_url("/v1/responses")
        assert url == "https://custom.example.com/v1/responses"

    def test_openresponses_build_url_falls_back_to_default(self) -> None:
        client = MagicMock(spec=OpenResponsesClient)
        client.base_url = None
        client._default_base_url = "https://api.openai.com"
        client._build_url = OpenResponsesClient._build_url.__get__(client)

        url = client._build_url("/v1/responses")
        assert url == "https://api.openai.com/v1/responses"

    def test_chatcompletions_build_url_uses_base_url(self) -> None:
        client = MagicMock(spec=ChatCompletionsClient)
        client.base_url = "https://api.minimax.io/anthropic"
        client._default_base_url = "https://api.anthropic.com"
        client._build_url = ChatCompletionsClient._build_url.__get__(client)

        url = client._build_url("/v1/chat/completions")
        assert url == "https://api.minimax.io/anthropic/v1/chat/completions"

    def test_chatcompletions_build_url_falls_back_to_default(self) -> None:
        client = MagicMock(spec=ChatCompletionsClient)
        client.base_url = None
        client._default_base_url = "https://api.anthropic.com"
        client._build_url = ChatCompletionsClient._build_url.__get__(client)

        url = client._build_url("/v1/chat/completions")
        assert url == "https://api.anthropic.com/v1/chat/completions"


class TestOllamaDefaultBaseUrl:
    """Test that Ollama clients use localhost:11434 by default."""

    def test_ollama_text_default_base_url(self) -> None:
        from celeste.modalities.text.providers.ollama.client import OllamaTextClient

        assert OllamaTextClient._default_base_url == "http://localhost:11434"
