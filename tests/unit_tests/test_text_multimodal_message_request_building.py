"""Unit tests for provider request building from multimodal messages."""

from pydantic import SecretStr

from celeste import (
    AudioPart,
    DocumentPart,
    ImagePart,
    Message,
    MessagePart,
    Model,
    Role,
    TextPart,
    ToolCall,
    VideoPart,
)
from celeste.artifacts import (
    AudioArtifact,
    DocumentArtifact,
    ImageArtifact,
    VideoArtifact,
)
from celeste.auth import AuthHeader
from celeste.core import Modality, Operation, Provider
from celeste.mime_types import (
    AudioMimeType,
    DocumentMimeType,
    ImageMimeType,
    VideoMimeType,
)
from celeste.modalities.text.io import TextInput
from celeste.modalities.text.providers.anthropic.client import AnthropicTextClient
from celeste.modalities.text.providers.cohere.client import CohereTextClient
from celeste.modalities.text.providers.google.client import GoogleTextClient
from celeste.modalities.text.providers.mistral.client import MistralTextClient
from celeste.modalities.text.providers.openai.client import OpenAITextClient


def _model(provider: Provider) -> Model:
    return Model(
        id="test-model",
        provider=provider,
        display_name="Test Model",
        operations={Modality.TEXT: {Operation.GENERATE}},
    )


def _auth(provider: Provider) -> AuthHeader:
    if provider == Provider.GOOGLE:
        return AuthHeader(secret=SecretStr("test"), header="x-goog-api-key", prefix="")
    if provider == Provider.ANTHROPIC:
        return AuthHeader(secret=SecretStr("test"), header="x-api-key", prefix="")
    return AuthHeader(secret=SecretStr("test"))


def _image() -> ImageArtifact:
    return ImageArtifact(data=b"img", mime_type=ImageMimeType.PNG)


def _document() -> DocumentArtifact:
    return DocumentArtifact(data=b"doc", mime_type=DocumentMimeType.PDF)


def _message(*parts: MessagePart) -> Message:
    return Message(role=Role.USER, content=list(parts))


def test_openai_message_parts_include_image_and_document_blocks() -> None:
    client = OpenAITextClient(
        model=_model(Provider.OPENAI),
        provider=Provider.OPENAI,
        auth=_auth(Provider.OPENAI),
    )

    request = client._init_request(
        TextInput(
            messages=[
                _message(
                    TextPart(text="inspect"),
                    ImagePart(image=_image()),
                    DocumentPart(document=_document()),
                )
            ]
        )
    )

    content = request["input"][0]["content"]
    assert content[0] == {"type": "input_text", "text": "inspect"}
    assert content[1]["type"] == "input_image"
    assert content[1]["image_url"].startswith("data:image/png;base64,")
    assert content[2]["type"] == "input_file"
    assert content[2]["file_data"].startswith("data:application/pdf;base64,")


def test_chat_completions_message_parts_include_image_and_document_blocks() -> None:
    client = MistralTextClient(
        model=_model(Provider.MISTRAL),
        provider=Provider.MISTRAL,
        auth=_auth(Provider.MISTRAL),
    )

    request = client._init_request(
        TextInput(
            messages=[
                _message(
                    ImagePart(image=_image()),
                    DocumentPart(document=_document()),
                    TextPart(text="inspect"),
                )
            ]
        )
    )

    content = request["messages"][0]["content"]
    assert content[0]["type"] == "image_url"
    assert content[0]["image_url"]["url"].startswith("data:image/png;base64,")
    assert content[1]["type"] == "document_url"
    assert content[1]["document_url"].startswith("data:application/pdf;base64,")
    assert content[2] == {"type": "text", "text": "inspect"}


def test_chat_completions_assistant_tool_call_serializes_message_parts() -> None:
    client = MistralTextClient(
        model=_model(Provider.MISTRAL),
        provider=Provider.MISTRAL,
        auth=_auth(Provider.MISTRAL),
    )

    request = client._init_request(
        TextInput(
            messages=[
                Message(
                    role=Role.ASSISTANT,
                    content=[TextPart(text="checking")],
                    tool_calls=[
                        ToolCall(
                            id="call_1",
                            name="lookup",
                            arguments={"query": "weather"},
                        )
                    ],
                )
            ]
        )
    )

    message = request["messages"][0]
    assert message["content"] == [{"type": "text", "text": "checking"}]
    assert message["tool_calls"][0]["function"]["name"] == "lookup"


def test_google_message_parts_include_all_media_blocks() -> None:
    client = GoogleTextClient(
        model=_model(Provider.GOOGLE),
        provider=Provider.GOOGLE,
        auth=_auth(Provider.GOOGLE),
    )

    request = client._init_request(
        TextInput(
            messages=[
                _message(
                    ImagePart(image=_image()),
                    VideoPart(
                        video=VideoArtifact(data=b"vid", mime_type=VideoMimeType.MP4)
                    ),
                    AudioPart(
                        audio=AudioArtifact(data=b"aud", mime_type=AudioMimeType.MP3)
                    ),
                    DocumentPart(document=_document()),
                    TextPart(text="inspect"),
                )
            ]
        )
    )

    parts = request["contents"][0]["parts"]
    assert [part.get("inline_data", {}).get("mime_type") for part in parts[:4]] == [
        "image/png",
        "video/mp4",
        "audio/mpeg",
        "application/pdf",
    ]
    assert parts[-1] == {"text": "inspect"}


def test_anthropic_message_parts_include_image_and_document_sources() -> None:
    client = AnthropicTextClient(
        model=_model(Provider.ANTHROPIC),
        provider=Provider.ANTHROPIC,
        auth=_auth(Provider.ANTHROPIC),
    )

    request = client._init_request(
        TextInput(
            messages=[
                _message(
                    ImagePart(image=_image()),
                    DocumentPart(document=_document()),
                    TextPart(text="inspect"),
                )
            ]
        )
    )

    content = request["messages"][0]["content"]
    assert content[0]["type"] == "image"
    assert content[0]["source"]["data"] == "aW1n"
    assert content[1]["type"] == "document"
    assert content[1]["source"]["data"] == "ZG9j"
    assert content[2] == {"type": "text", "text": "inspect"}


def test_cohere_message_parts_include_image_block() -> None:
    client = CohereTextClient(
        model=_model(Provider.COHERE),
        provider=Provider.COHERE,
        auth=_auth(Provider.COHERE),
    )

    request = client._init_request(
        TextInput(messages=[_message(ImagePart(image=_image()), TextPart(text="look"))])
    )

    content = request["messages"][0]["content"]
    assert content[0]["type"] == "image_url"
    assert content[0]["image_url"]["url"].startswith("data:image/png;base64,")
    assert content[1] == {"type": "text", "text": "look"}


def test_openresponses_assistant_tool_call_preserves_message_content() -> None:
    client = OpenAITextClient(
        model=_model(Provider.OPENAI),
        provider=Provider.OPENAI,
        auth=_auth(Provider.OPENAI),
    )

    request = client._init_request(
        TextInput(
            messages=[
                Message(
                    role=Role.ASSISTANT,
                    content=[TextPart(text="checking")],
                    tool_calls=[
                        ToolCall(
                            id="call_1",
                            name="lookup",
                            arguments={"query": "weather"},
                        )
                    ],
                )
            ]
        )
    )

    assert request["input"][0] == {
        "role": "assistant",
        "content": [{"type": "input_text", "text": "checking"}],
    }
    assert request["input"][1]["type"] == "function_call"
    assert request["input"][1]["name"] == "lookup"
