"""Unit tests for `TextClient.analyze(image=...)` request building (no network)."""

import inspect

from pydantic import SecretStr

from celeste import Model
from celeste.artifacts import ImageArtifact
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import ImageMimeType
from celeste.modalities.text.io import TextInput
from celeste.modalities.text.providers.anthropic.client import AnthropicTextClient
from celeste.modalities.text.providers.cohere.client import CohereTextClient
from celeste.modalities.text.providers.google.client import GoogleTextClient
from celeste.modalities.text.providers.groq.client import GroqTextClient
from celeste.modalities.text.providers.mistral.client import MistralTextClient
from celeste.modalities.text.providers.moonshot.client import MoonshotTextClient
from celeste.modalities.text.providers.openai.client import OpenAITextClient
from celeste.modalities.text.providers.xai.client import XAITextClient


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


def test_openai_init_request_includes_input_image_block() -> None:
    model = Model(
        id="gpt-4o",
        provider=Provider.OPENAI,
        display_name="GPT-4o",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
    )
    client = OpenAITextClient(
        model=model,
        provider=Provider.OPENAI,
        auth=AuthHeader(secret=SecretStr("test")),
    )

    request = client._init_request(
        TextInput(
            prompt="Describe the image",
            image=ImageArtifact(data=b"abc", mime_type=ImageMimeType.PNG),
        )
    )

    content = request["input"][0]["content"]
    assert content[0]["type"] == "input_image"
    assert content[0]["image_url"].startswith("data:image/")
    assert content[-1] == {"type": "input_text", "text": "Describe the image"}


def test_google_init_request_includes_inline_data_part() -> None:
    model = Model(
        id="gemini-2.5-pro",
        provider=Provider.GOOGLE,
        display_name="Gemini 2.5 Pro",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
    )
    client = GoogleTextClient(
        model=model,
        provider=Provider.GOOGLE,
        auth=AuthHeader(secret=SecretStr("test"), header="x-goog-api-key", prefix=""),
    )

    request = client._init_request(
        TextInput(
            prompt="Describe the image",
            image=ImageArtifact(data=b"abc", mime_type=ImageMimeType.PNG),
        )
    )

    parts = request["contents"][0]["parts"]
    assert "inline_data" in parts[0]
    assert parts[0]["inline_data"]["data"] == "YWJj"
    assert parts[-1] == {"text": "Describe the image"}


def test_mistral_init_request_includes_image_url_block() -> None:
    model = Model(
        id="pixtral-12b-latest",
        provider=Provider.MISTRAL,
        display_name="Pixtral 12B",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
    )
    client = MistralTextClient(
        model=model,
        provider=Provider.MISTRAL,
        auth=AuthHeader(secret=SecretStr("test")),
    )

    request = client._init_request(
        TextInput(
            prompt="Describe the image",
            image=ImageArtifact(data=b"abc", mime_type=ImageMimeType.PNG),
        )
    )

    content = request["messages"][0]["content"]
    assert content[0]["type"] == "image_url"
    assert content[0]["image_url"]["url"].startswith("data:image/")
    assert content[-1] == {"type": "text", "text": "Describe the image"}


def test_anthropic_init_request_includes_image_source_block() -> None:
    model = Model(
        id="claude-sonnet-4-5",
        provider=Provider.ANTHROPIC,
        display_name="Claude Sonnet 4.5",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
    )
    client = AnthropicTextClient(
        model=model,
        provider=Provider.ANTHROPIC,
        auth=AuthHeader(secret=SecretStr("test"), header="x-api-key", prefix=""),
    )

    request = client._init_request(
        TextInput(
            prompt="Describe the image",
            image=ImageArtifact(data=b"abc", mime_type=ImageMimeType.PNG),
        )
    )

    content = request["messages"][0]["content"]
    assert content[0]["type"] == "image"
    assert content[0]["source"]["type"] == "base64"
    assert content[0]["source"]["data"] == "YWJj"
    assert content[-1] == {"type": "text", "text": "Describe the image"}


def test_cohere_init_request_includes_image_url_block() -> None:
    model = Model(
        id="command-a-vision-07-2025",
        provider=Provider.COHERE,
        display_name="Command A Vision",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
    )
    client = CohereTextClient(
        model=model,
        provider=Provider.COHERE,
        auth=AuthHeader(secret=SecretStr("test")),
    )

    request = client._init_request(
        TextInput(
            prompt="Describe the image",
            image=ImageArtifact(data=b"abc", mime_type=ImageMimeType.PNG),
        )
    )

    content = request["messages"][0]["content"]
    assert content[0]["type"] == "image_url"
    assert content[0]["image_url"]["url"].startswith("data:image/")
    assert content[-1] == {"type": "text", "text": "Describe the image"}


def test_groq_init_request_includes_image_url_block() -> None:
    model = Model(
        id="llama-3.2-11b-vision-preview",
        provider=Provider.GROQ,
        display_name="Llama 3.2 11B Vision",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
    )
    client = GroqTextClient(
        model=model,
        provider=Provider.GROQ,
        auth=AuthHeader(secret=SecretStr("test")),
    )

    request = client._init_request(
        TextInput(
            prompt="Describe the image",
            image=ImageArtifact(data=b"abc", mime_type=ImageMimeType.PNG),
        )
    )

    content = request["messages"][0]["content"]
    assert content[0]["type"] == "image_url"
    assert content[0]["image_url"]["url"].startswith("data:image/")
    assert content[-1] == {"type": "text", "text": "Describe the image"}


def test_moonshot_init_request_includes_image_url_block() -> None:
    model = Model(
        id="moonshot-v1-8k-vision-preview",
        provider=Provider.MOONSHOT,
        display_name="Moonshot v1 8K Vision",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
    )
    client = MoonshotTextClient(
        model=model,
        provider=Provider.MOONSHOT,
        auth=AuthHeader(secret=SecretStr("test")),
    )

    request = client._init_request(
        TextInput(
            prompt="Describe the image",
            image=ImageArtifact(data=b"abc", mime_type=ImageMimeType.PNG),
        )
    )

    content = request["messages"][0]["content"]
    assert content[0]["type"] == "image_url"
    assert content[0]["image_url"]["url"].startswith("data:image/")
    assert content[-1] == {"type": "text", "text": "Describe the image"}


def test_xai_init_request_includes_input_image_block() -> None:
    model = Model(
        id="grok-4-0709",
        provider=Provider.XAI,
        display_name="Grok 4",
        operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
    )
    client = XAITextClient(
        model=model,
        provider=Provider.XAI,
        auth=AuthHeader(secret=SecretStr("test")),
    )

    request = client._init_request(
        TextInput(
            prompt="Describe the image",
            image=ImageArtifact(data=b"abc", mime_type=ImageMimeType.PNG),
        )
    )

    # Responses API format: input is array of message objects with content
    content = request["input"][0]["content"]
    assert content[0]["type"] == "input_image"
    assert content[0]["image_url"].startswith("data:image/")
    assert content[-1] == {"type": "input_text", "text": "Describe the image"}
