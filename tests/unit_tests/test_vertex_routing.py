"""Vertex and direct API URL routing contracts."""

from typing import Any
from unittest.mock import MagicMock

import pytest
from pydantic import SecretStr

from celeste.auth import AuthHeader
from celeste.core import Provider
from celeste.modalities.text.io import TextInput
from celeste.modalities.text.providers.anthropic.client import AnthropicTextClient
from celeste.models import Model
from celeste.providers.anthropic.messages import config as anthropic_config
from celeste.providers.anthropic.messages.client import AnthropicMessagesClient
from celeste.providers.deepseek.chat import config as deepseek_config
from celeste.providers.deepseek.chat.client import DeepSeekChatClient
from celeste.providers.google.auth import GoogleADC
from celeste.providers.google.embeddings import config as embeddings_config
from celeste.providers.google.embeddings.client import GoogleEmbeddingsClient
from celeste.providers.google.generate_content import config as generate_config
from celeste.providers.google.generate_content.client import GoogleGenerateContentClient
from celeste.providers.google.imagen import config as imagen_config
from celeste.providers.google.imagen.client import GoogleImagenClient
from celeste.providers.google.veo import config as veo_config
from celeste.providers.google.veo.client import GoogleVeoClient
from celeste.providers.mistral.chat import config as mistral_config
from celeste.providers.mistral.chat.client import MistralChatClient
from celeste.tools import WebSearch


def _model(model_id: str) -> Model:
    return Model(id=model_id, provider=Provider.GOOGLE, display_name=model_id)


def _api_key() -> AuthHeader:
    return AuthHeader(secret=SecretStr("test"), header="x-goog-api-key", prefix="")


def _adc(
    *, project_id: str | None = "test-project", location: str = "us-central1"
) -> GoogleADC:
    auth = GoogleADC(project_id=project_id, location=location)
    object.__setattr__(auth, "_credentials", MagicMock(valid=True, token=None))
    object.__setattr__(auth, "_project", None)
    return auth


def _build_url(
    client_type: type[Any],
    endpoint: str,
    model_id: str,
    auth: AuthHeader | GoogleADC,
    *,
    streaming: bool = False,
) -> str:
    client = MagicMock(auth=auth, model=_model(model_id))
    if hasattr(client_type, "_get_vertex_endpoint"):
        client._get_vertex_endpoint = client_type._get_vertex_endpoint.__get__(client)
    method = client_type._build_url.__get__(client)
    if client_type in (AnthropicMessagesClient, MistralChatClient, DeepSeekChatClient):
        return method(endpoint, streaming=streaming)
    return method(endpoint)


@pytest.mark.parametrize(
    ("location", "expected"),
    [
        ("global", "https://aiplatform.googleapis.com"),
        ("europe-west4", "https://europe-west4-aiplatform.googleapis.com"),
    ],
)
def test_vertex_base_url(location: str, expected: str) -> None:
    assert GoogleADC(location=location).get_vertex_base_url() == expected


def test_explicit_project_does_not_load_adc() -> None:
    assert GoogleADC(project_id="explicit").resolved_project_id == "explicit"


def test_adc_project_is_used_when_not_explicit() -> None:
    auth = _adc(project_id=None)
    object.__setattr__(auth, "_project", "discovered")
    assert auth.resolved_project_id == "discovered"


def test_vertex_url_requires_project() -> None:
    with pytest.raises(ValueError, match="requires a project_id"):
        _adc(project_id=None).build_url("/projects/{project_id}/{location}")


@pytest.mark.parametrize(
    ("client_type", "endpoint", "model_id", "expected"),
    [
        (
            GoogleGenerateContentClient,
            generate_config.GoogleGenerateContentEndpoint.GENERATE_CONTENT,
            "gemini-2.0-flash",
            "generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        ),
        (
            AnthropicMessagesClient,
            anthropic_config.AnthropicMessagesEndpoint.CREATE_MESSAGE,
            "claude-sonnet-4-5",
            "api.anthropic.com/v1/messages",
        ),
        (
            GoogleImagenClient,
            imagen_config.GoogleImagenEndpoint.CREATE_IMAGE,
            "imagen-4.0-generate-001",
            "generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict",
        ),
        (
            GoogleEmbeddingsClient,
            embeddings_config.GoogleEmbeddingsEndpoint.EMBED_CONTENT,
            "gemini-embedding-2",
            "generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent",
        ),
        (
            GoogleVeoClient,
            veo_config.GoogleVeoEndpoint.CREATE_VIDEO,
            "veo-3.1-generate-preview",
            "generativelanguage.googleapis.com/v1beta/models/veo-3.1-generate-preview:predictLongRunning",
        ),
        (
            MistralChatClient,
            mistral_config.MistralChatEndpoint.CREATE_CHAT_COMPLETION,
            "mistral-large-2411",
            "api.mistral.ai/v1/chat/completions",
        ),
        (
            DeepSeekChatClient,
            deepseek_config.DeepSeekChatEndpoint.CREATE_CHAT,
            "deepseek-chat",
            "api.deepseek.com/v1/chat/completions",
        ),
    ],
)
def test_api_key_routes_directly(
    client_type: type[Any], endpoint: str, model_id: str, expected: str
) -> None:
    assert expected in _build_url(client_type, endpoint, model_id, _api_key())


@pytest.mark.parametrize(
    ("client_type", "endpoint", "model_id", "fragments"),
    [
        (
            GoogleGenerateContentClient,
            generate_config.GoogleGenerateContentEndpoint.GENERATE_CONTENT,
            "gemini-2.0-flash",
            ("projects/test-project", "publishers/google", "gemini-2.0-flash"),
        ),
        (
            AnthropicMessagesClient,
            anthropic_config.AnthropicMessagesEndpoint.CREATE_MESSAGE,
            "claude-sonnet-4-5",
            ("projects/test-project", "publishers/anthropic", "rawPredict"),
        ),
        (
            GoogleImagenClient,
            imagen_config.GoogleImagenEndpoint.CREATE_IMAGE,
            "imagen-4.0-generate-001",
            ("projects/test-project", "publishers/google", "imagen-4.0-generate-001"),
        ),
        (
            GoogleVeoClient,
            veo_config.GoogleVeoEndpoint.CREATE_VIDEO,
            "veo-3.1-generate-preview",
            ("projects/test-project", "publishers/google", "veo-3.1-generate-preview"),
        ),
        (
            MistralChatClient,
            mistral_config.MistralChatEndpoint.CREATE_CHAT_COMPLETION,
            "mistral-large-2411",
            ("projects/test-project", "publishers/mistralai", "rawPredict"),
        ),
        (
            DeepSeekChatClient,
            deepseek_config.DeepSeekChatEndpoint.CREATE_CHAT,
            "deepseek-chat",
            ("projects/test-project", "endpoints/openapi/chat/completions"),
        ),
    ],
)
def test_adc_routes_through_vertex(
    client_type: type[Any], endpoint: str, model_id: str, fragments: tuple[str, ...]
) -> None:
    url = _build_url(client_type, endpoint, model_id, _adc())
    assert url.startswith("https://us-central1-aiplatform.googleapis.com")
    assert all(fragment in url for fragment in fragments)


@pytest.mark.parametrize(
    ("client_type", "endpoint", "model_id"),
    [
        (
            AnthropicMessagesClient,
            anthropic_config.AnthropicMessagesEndpoint.CREATE_MESSAGE,
            "claude-sonnet-4-5",
        ),
        (
            MistralChatClient,
            mistral_config.MistralChatEndpoint.CREATE_CHAT_COMPLETION,
            "mistral-large-2411",
        ),
    ],
)
def test_vertex_streaming_uses_stream_endpoint(
    client_type: type[Any], endpoint: str, model_id: str
) -> None:
    assert "streamRawPredict" in _build_url(
        client_type, endpoint, model_id, _adc(), streaming=True
    )


def test_anthropic_vertex_uses_url_model_and_body_version(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(GoogleADC, "get_headers", lambda self: {})
    client = AnthropicTextClient(
        model=_model("claude-opus-5"),
        provider=Provider.ANTHROPIC,
        auth=_adc(),
    )

    request = client._build_request(
        TextInput(prompt="hello"), extra_body={"model": "body-override"}
    )

    assert request["anthropic_version"] == "vertex-2023-10-16"
    assert "model" not in request
    assert anthropic_config.HEADER_ANTHROPIC_VERSION not in client._build_headers()


def test_anthropic_direct_request_keeps_model_and_version_header() -> None:
    client = AnthropicTextClient(
        model=_model("claude-opus-5"),
        provider=Provider.ANTHROPIC,
        auth=_api_key(),
    )

    request = client._build_request(TextInput(prompt="hello"))

    assert request["model"] == "claude-opus-5"
    assert client._build_headers()[anthropic_config.HEADER_ANTHROPIC_VERSION] == (
        anthropic_config.ANTHROPIC_VERSION
    )


def test_anthropic_web_search_version_respects_serving_route() -> None:
    direct = AnthropicTextClient(
        model=_model("claude-opus-5"),
        provider=Provider.ANTHROPIC,
        auth=_api_key(),
    )
    vertex = AnthropicTextClient(
        model=_model("claude-opus-5"),
        provider=Provider.ANTHROPIC,
        auth=_adc(),
    )

    assert (
        direct._build_request(TextInput(prompt="hello"), tools=[WebSearch()])["tools"][
            0
        ]["type"]
        == "web_search_20260209"
    )
    assert (
        vertex._build_request(TextInput(prompt="hello"), tools=[WebSearch()])["tools"][
            0
        ]["type"]
        == "web_search"
    )


def test_anthropic_raw_web_search_tool_is_not_rewritten() -> None:
    client = AnthropicTextClient(
        model=_model("claude-opus-5"),
        provider=Provider.ANTHROPIC,
        auth=_api_key(),
    )
    raw = {
        "type": "web_search_20260318",
        "name": "web_search",
        "response_inclusion": "search_results",
    }

    assert client._build_request(TextInput(prompt="hello"), tools=[raw])["tools"] == [
        raw
    ]


def test_anthropic_vertex_prompt_feedback_is_an_error() -> None:
    client = AnthropicTextClient(
        model=_model("claude-opus-5"),
        provider=Provider.ANTHROPIC,
        auth=_adc(),
    )

    with pytest.raises(ValueError, match="PROHIBTED_CONTENT"):
        client._parse_content({"promptFeedback": {"blockReason": "PROHIBTED_CONTENT"}})


@pytest.mark.parametrize(
    ("location", "base_url"),
    [
        ("global", "https://aiplatform.googleapis.com"),
        ("us", "https://aiplatform.us.rep.googleapis.com"),
        ("eu", "https://aiplatform.eu.rep.googleapis.com"),
        ("us-central1", "https://us-central1-aiplatform.googleapis.com"),
    ],
)
def test_adc_embeddings_use_location_endpoint(location: str, base_url: str) -> None:
    url = _build_url(
        GoogleEmbeddingsClient,
        embeddings_config.GoogleEmbeddingsEndpoint.EMBED_CONTENT,
        "gemini-embedding-2",
        _adc(location=location),
    )

    assert url.startswith(f"{base_url}/v1/")
    assert f"/locations/{location}/" in url
    assert url.endswith("/models/gemini-embedding-2:embedContent")


def test_veo_poll_routes_match_auth() -> None:
    direct = MagicMock(auth=_api_key(), model=_model("veo"))
    vertex = MagicMock(auth=_adc(), model=_model("veo"))
    direct_url = GoogleVeoClient._build_poll_url(direct, "operations/abc")
    vertex_url = GoogleVeoClient._build_poll_url(vertex, "operations/abc")
    assert direct_url.endswith("/v1beta/operations/abc")
    assert "fetchPredictOperation" in vertex_url
