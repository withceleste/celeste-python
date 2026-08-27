"""Unit tests for `TextClient.analyze(image=...)` request building (no network)."""

import inspect

import pytest
from pydantic import SecretStr

from celeste import Model
from celeste.artifacts import ImageArtifact
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import ImageMimeType
from celeste.modalities.text.client import TextClient
from celeste.modalities.text.io import TextInput
from celeste.modalities.text.providers.anthropic.client import AnthropicTextClient
from celeste.modalities.text.providers.cohere.client import CohereTextClient
from celeste.modalities.text.providers.google.client import GoogleTextClient
from celeste.modalities.text.providers.groq.client import GroqTextClient
from celeste.modalities.text.providers.mistral.client import MistralTextClient
from celeste.modalities.text.providers.moonshot.client import MoonshotTextClient
from celeste.modalities.text.providers.openai.client import OpenAITextClient
from celeste.modalities.text.providers.xai.client import XAITextClient

IMAGE_INPUT = TextInput(
    prompt="Describe the image",
    image=ImageArtifact(data=b"abc", mime_type=ImageMimeType.PNG),
)


def _client(
    client_cls: type[TextClient], provider: Provider, model_id: str
) -> TextClient:
    header = {
        Provider.GOOGLE: {"header": "x-goog-api-key", "prefix": ""},
        Provider.ANTHROPIC: {"header": "x-api-key", "prefix": ""},
    }.get(provider, {})
    return client_cls(
        model=Model(
            id=model_id,
            provider=provider,
            display_name=model_id,
            operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        ),
        provider=provider,
        auth=AuthHeader(secret=SecretStr("test"), **header),
    )


def test_analyze_signatures_accept_image() -> None:
    """Ensure all providers accept `image=` (all optional)."""
    for client_cls in (
        OpenAITextClient,
        GoogleTextClient,
        MistralTextClient,
        AnthropicTextClient,
        CohereTextClient,
        GroqTextClient,
        MoonshotTextClient,
        XAITextClient,
    ):
        sig = inspect.signature(client_cls.analyze)
        params = sig.parameters

        # image is optional keyword-only parameter
        assert "image" in params
        assert params["image"].default is None  # optional

        # No text parameter
        assert "text" not in params


def test_google_analyze_signature_accepts_video_and_audio() -> None:
    """Ensure Google provider accepts `video=` and `audio=` (only Google supports native video/audio)."""
    sig = inspect.signature(GoogleTextClient.analyze)
    params = sig.parameters

    assert "video" in params
    assert params["video"].default is None  # optional
    assert "audio" in params
    assert params["audio"].default is None  # optional


@pytest.mark.parametrize(
    ("client_cls", "provider", "model_id"),
    [
        (OpenAITextClient, Provider.OPENAI, "gpt-4o"),
        (XAITextClient, Provider.XAI, "grok-4.20-0309-reasoning"),
    ],
)
def test_openresponses_init_request_includes_input_image_block(
    client_cls: type[TextClient], provider: Provider, model_id: str
) -> None:
    client = _client(client_cls, provider, model_id)

    request = client._init_request(IMAGE_INPUT)

    content = request["input"][0]["content"]
    assert content[0]["type"] == "input_image"
    assert content[0]["image_url"].startswith("data:image/")
    assert content[-1] == {"type": "input_text", "text": "Describe the image"}


def test_google_init_request_includes_image_content_part() -> None:
    client = _client(GoogleTextClient, Provider.GOOGLE, "gemini-2.5-pro")

    request = client._init_request(IMAGE_INPUT)

    parts = request["input"][0]["content"]
    assert parts[0]["type"] == "image"
    assert parts[0]["data"] == "YWJj"
    assert parts[-1] == {"type": "text", "text": "Describe the image"}


@pytest.mark.parametrize(
    ("client_cls", "provider", "model_id"),
    [
        (MistralTextClient, Provider.MISTRAL, "pixtral-12b-latest"),
        (CohereTextClient, Provider.COHERE, "command-a-vision-07-2025"),
        (GroqTextClient, Provider.GROQ, "llama-3.2-11b-vision-preview"),
        (MoonshotTextClient, Provider.MOONSHOT, "moonshot-v1-8k-vision-preview"),
    ],
)
def test_chat_completions_init_request_includes_image_url_block(
    client_cls: type[TextClient], provider: Provider, model_id: str
) -> None:
    client = _client(client_cls, provider, model_id)

    request = client._init_request(IMAGE_INPUT)

    content = request["messages"][0]["content"]
    assert content[0]["type"] == "image_url"
    assert content[0]["image_url"]["url"].startswith("data:image/")
    assert content[-1] == {"type": "text", "text": "Describe the image"}


def test_anthropic_init_request_includes_image_source_block() -> None:
    client = _client(AnthropicTextClient, Provider.ANTHROPIC, "claude-sonnet-4-5")

    request = client._init_request(IMAGE_INPUT)

    content = request["messages"][0]["content"]
    assert content[0]["type"] == "image"
    assert content[0]["source"]["type"] == "base64"
    assert content[0]["source"]["data"] == "YWJj"
    assert content[-1] == {"type": "text", "text": "Describe the image"}
