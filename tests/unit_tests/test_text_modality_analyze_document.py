"""Unit tests for `TextClient.analyze(document=...)` request building (no network)."""

from typing import Any

import pytest
from pydantic import SecretStr

from celeste import Model
from celeste.artifacts import DocumentArtifact
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import DocumentMimeType
from celeste.modalities.text.io import TextInput
from celeste.modalities.text.providers.anthropic.client import AnthropicTextClient
from celeste.modalities.text.providers.google.interactions import (
    GoogleInteractionsTextClient,
)
from celeste.modalities.text.providers.mistral.client import MistralTextClient
from celeste.modalities.text.providers.openai.client import OpenAITextClient

PROMPT = "Summarize this document"
PDF = DocumentArtifact(data=b"abc", mime_type=DocumentMimeType.PDF)
PDF_DATA_URL = "data:application/pdf;base64,YWJj"
PDF_URL = "https://example.com/doc.pdf"

# Provider -> (client class, model id, request key, prompt part type).
_CLIENTS = {
    Provider.OPENAI: (OpenAITextClient, "gpt-4o", "input", "input_text"),
    Provider.GOOGLE: (GoogleInteractionsTextClient, "gemini-2.5-pro", "input", "text"),
    Provider.ANTHROPIC: (AnthropicTextClient, "claude-sonnet-4-5", "messages", "text"),
    Provider.MISTRAL: (MistralTextClient, "pixtral-12b-latest", "messages", "text"),
}
_HEADERS = {
    Provider.GOOGLE: {"header": "x-goog-api-key", "prefix": ""},
    Provider.ANTHROPIC: {"header": "x-api-key", "prefix": ""},
}


@pytest.mark.parametrize(
    ("provider", "document", "block"),
    [
        (
            Provider.OPENAI,
            PDF,
            {"type": "input_file", "filename": "document", "file_data": PDF_DATA_URL},
        ),
        (
            Provider.GOOGLE,
            PDF,
            {"type": "document", "mime_type": "application/pdf", "data": "YWJj"},
        ),
        (
            Provider.ANTHROPIC,
            PDF,
            {
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": "YWJj",
                },
            },
        ),
        (
            Provider.MISTRAL,
            PDF,
            {"type": "document_url", "document_url": PDF_DATA_URL},
        ),
        (
            Provider.OPENAI,
            DocumentArtifact(url=PDF_URL),
            {"type": "input_file", "file_url": PDF_URL},
        ),
        (
            Provider.GOOGLE,
            DocumentArtifact(url=PDF_URL, mime_type=DocumentMimeType.PDF),
            {"type": "document", "uri": PDF_URL, "mime_type": "application/pdf"},
        ),
    ],
    ids=["openai", "google", "anthropic", "mistral", "openai-url", "google-url"],
)
def test_init_request_puts_document_block_before_prompt(
    provider: Provider, document: DocumentArtifact, block: dict[str, Any]
) -> None:
    client_cls, model_id, key, prompt_type = _CLIENTS[provider]
    client = client_cls(
        model=Model(
            id=model_id,
            provider=provider,
            display_name=model_id,
            operations={Modality.TEXT: {Operation.GENERATE, Operation.ANALYZE}},
        ),
        provider=provider,
        auth=AuthHeader(secret=SecretStr("test"), **_HEADERS.get(provider, {})),
    )

    request = client._init_request(TextInput(prompt=PROMPT, document=document))

    assert request[key][0]["content"] == [block, {"type": prompt_type, "text": PROMPT}]
