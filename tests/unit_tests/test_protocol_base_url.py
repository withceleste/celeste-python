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


@pytest.mark.parametrize(
    ("protocol", "client_type", "auth_type", "api_key"),
    [
        (Protocol.OPENRESPONSES, OpenResponsesTextClient, NoAuth, None),
        (Protocol.CHATCOMPLETIONS, ChatCompletionsTextClient, AuthHeader, "key"),
    ],
)
def test_protocol_resolves_client_and_auth(
    protocol: Protocol,
    client_type: type,
    auth_type: type,
    api_key: str | None,
) -> None:
    client = create_client(
        protocol=protocol,
        base_url="https://example.com",
        model="unregistered-model",
        modality="text",
        operation="generate",
        api_key=api_key,
    )

    assert isinstance(client, client_type)
    assert isinstance(client.auth, auth_type)
    assert client.protocol is protocol
    assert client.provider is None
    assert client.base_url == "https://example.com"


def test_base_url_defaults_to_openresponses_protocol() -> None:
    client = create_client(
        base_url="http://localhost:11434",
        model="unregistered-model",
        modality="text",
        operation="generate",
    )
    assert isinstance(client, OpenResponsesTextClient)
    assert client.protocol is Protocol.OPENRESPONSES


def test_provider_accepts_custom_model_and_base_url() -> None:
    with pytest.warns(UserWarning, match="not registered"):
        client = create_client(
            provider="openai",
            base_url="https://proxy.example.com",
            model="unregistered-model",
            modality="text",
            operation="generate",
            api_key="key",
        )
    assert client.base_url == "https://proxy.example.com"


def test_missing_protocol_provider_and_base_url_is_rejected() -> None:
    with pytest.raises(ModelNotFoundError):
        create_client(
            model="unregistered-model",
            modality="text",
            operation="generate",
        )


@pytest.mark.parametrize(
    ("client_type", "base_url", "default", "expected"),
    [
        (
            OpenResponsesClient,
            "https://custom.example.com",
            "https://default.example.com",
            "https://custom.example.com/v1/responses",
        ),
        (
            OpenResponsesClient,
            None,
            "https://default.example.com",
            "https://default.example.com/v1/responses",
        ),
        (
            ChatCompletionsClient,
            "https://custom.example.com",
            "https://default.example.com",
            "https://custom.example.com/v1/chat/completions",
        ),
        (
            ChatCompletionsClient,
            None,
            "https://default.example.com",
            "https://default.example.com/v1/chat/completions",
        ),
    ],
)
def test_protocol_url_uses_override_then_default(
    client_type: type, base_url: str | None, default: str, expected: str
) -> None:
    client = MagicMock(spec=client_type)
    client.base_url = base_url
    client._default_base_url = default
    client._build_url = client_type._build_url.__get__(client)
    endpoint = (
        "/v1/responses"
        if client_type is OpenResponsesClient
        else "/v1/chat/completions"
    )
    assert client._build_url(endpoint) == expected
