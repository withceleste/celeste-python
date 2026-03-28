"""Unit tests for `TextClient.analyze(document=...)` request building (no network)."""

import inspect

from pydantic import SecretStr

from celeste import Model
from celeste.artifacts import DocumentArtifact
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import DocumentMimeType
from celeste.modalities.text.client import TextClient
from celeste.modalities.text.io import TextInput
from celeste.modalities.text.providers.anthropic.client import AnthropicTextClient
from celeste.modalities.text.providers.google.client import GoogleTextClient
from celeste.modalities.text.providers.mistral.client import MistralTextClient
from celeste.modalities.text.providers.openai.client import OpenAITextClient


def test_analyze_signature_accepts_document() -> None:
    """Ensure base TextClient.analyze() accepts `document=` (optional)."""
    sig = inspect.signature(TextClient.analyze)
    params = sig.parameters

    assert "document" in params, "TextClient.analyze missing document param"
    assert params["document"].default is None


def test_openai_init_request_includes_input_file_block() -> None:
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
            prompt="Summarize this document",
            document=DocumentArtifact(data=b"abc", mime_type=DocumentMimeType.PDF),
        )
    )

    content = request["input"][0]["content"]
    assert content[0]["type"] == "input_file"
    assert content[0]["file_data"].startswith("data:application/pdf;base64,")
    assert content[-1] == {"type": "input_text", "text": "Summarize this document"}


def test_google_init_request_includes_document_part() -> None:
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
            prompt="Summarize this document",
            document=DocumentArtifact(data=b"abc", mime_type=DocumentMimeType.PDF),
        )
    )

    parts = request["contents"][0]["parts"]
    assert "inline_data" in parts[0]
    assert parts[0]["inline_data"]["mime_type"] == "application/pdf"
    assert parts[0]["inline_data"]["data"] == "YWJj"
    assert parts[-1] == {"text": "Summarize this document"}


def test_anthropic_init_request_includes_document_block() -> None:
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
            prompt="Summarize this document",
            document=DocumentArtifact(data=b"abc", mime_type=DocumentMimeType.PDF),
        )
    )

    content = request["messages"][0]["content"]
    assert content[0]["type"] == "document"
    assert content[0]["source"]["type"] == "base64"
    assert content[0]["source"]["media_type"] == "application/pdf"
    assert content[0]["source"]["data"] == "YWJj"
    assert content[-1] == {"type": "text", "text": "Summarize this document"}


def test_mistral_init_request_includes_document_url_block() -> None:
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
            prompt="Summarize this document",
            document=DocumentArtifact(data=b"abc", mime_type=DocumentMimeType.PDF),
        )
    )

    content = request["messages"][0]["content"]
    assert content[0]["type"] == "document_url"
    assert content[0]["document_url"].startswith("data:application/pdf;base64,")
    assert content[-1] == {"type": "text", "text": "Summarize this document"}
