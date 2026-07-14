"""Provider document URL serialization not covered by inline-media cases."""

import pytest
from pydantic import SecretStr

from celeste.artifacts import DocumentArtifact
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import DocumentMimeType
from celeste.modalities.text.io import TextInput
from celeste.modalities.text.providers.google.client import GoogleTextClient
from celeste.modalities.text.providers.openai.client import OpenAITextClient
from celeste.models import Model


def _model(provider: Provider) -> Model:
    return Model(
        id="test",
        provider=provider,
        display_name="test",
        operations={Modality.TEXT: {Operation.ANALYZE}},
    )


@pytest.mark.parametrize("provider", [Provider.OPENAI, Provider.GOOGLE])
def test_document_url_is_preserved(provider: Provider) -> None:
    auth = AuthHeader(
        secret=SecretStr("test"),
        header="x-goog-api-key" if provider == Provider.GOOGLE else "Authorization",
        prefix="" if provider == Provider.GOOGLE else "Bearer ",
    )
    client = (
        GoogleTextClient(model=_model(provider), provider=provider, auth=auth)
        if provider == Provider.GOOGLE
        else OpenAITextClient(model=_model(provider), provider=provider, auth=auth)
    )
    request = client._init_request(
        TextInput(
            prompt="summarize",
            document=DocumentArtifact(
                url="https://example.com/doc.pdf", mime_type=DocumentMimeType.PDF
            ),
        )
    )

    if provider == Provider.GOOGLE:
        block = request["contents"][0]["parts"][0]["file_data"]
        assert block == {
            "file_uri": "https://example.com/doc.pdf",
            "mime_type": "application/pdf",
        }
    else:
        block = request["input"][0]["content"][0]
        assert block["type"] == "input_file"
        assert block["file_url"] == "https://example.com/doc.pdf"
        assert "file_data" not in block
