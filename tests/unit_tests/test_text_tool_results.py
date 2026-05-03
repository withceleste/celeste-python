"""Unit tests for text tool-result request payloads."""

import json

from pydantic import BaseModel, SecretStr

from celeste import Message, Model, Role
from celeste.auth import AuthHeader
from celeste.core import InputType, Modality, Operation, Provider
from celeste.modalities.text.io import TextInput
from celeste.modalities.text.protocols.chatcompletions.client import (
    ChatCompletionsTextClient,
)
from celeste.modalities.text.protocols.openresponses.client import (
    OpenResponsesTextClient,
)
from celeste.modalities.text.providers.anthropic.client import AnthropicTextClient
from celeste.modalities.text.providers.cohere.client import CohereTextClient
from celeste.modalities.text.providers.google.client import GoogleTextClient
from celeste.tools import ToolOutput, ToolResult


class ArtifactRef(BaseModel):
    id: str
    artifact_type: InputType


def _text_model(provider: Provider) -> Model:
    return Model(
        id="test-model",
        provider=provider,
        display_name="Test Model",
        operations={Modality.TEXT: {Operation.GENERATE}},
    )


def _artifact_output() -> ToolOutput[ArtifactRef]:
    return ToolOutput[ArtifactRef](
        content=ArtifactRef(id="image-1", artifact_type=InputType.IMAGE),
        metadata={"provider": "test"},
    )


def _tool_result(content: object) -> ToolResult:
    return ToolResult(
        content=content,
        tool_call_id="call_123",
        name="generate_image",
    )


def test_chat_completions_tool_result_uses_pydantic_json_text() -> None:
    output = _artifact_output()
    client = ChatCompletionsTextClient(
        model=_text_model(Provider.OPENAI),
        provider=Provider.OPENAI,
        auth=AuthHeader(secret=SecretStr("test")),
    )

    request = client._init_request(TextInput(messages=[_tool_result(output)]))

    content = request["messages"][0]["content"]
    assert content == output.model_dump_json()
    assert json.loads(content) == output.model_dump(mode="json")


def test_chat_completions_tool_result_preserves_string_content() -> None:
    client = ChatCompletionsTextClient(
        model=_text_model(Provider.OPENAI),
        provider=Provider.OPENAI,
        auth=AuthHeader(secret=SecretStr("test")),
    )

    request = client._init_request(TextInput(messages=[_tool_result("done")]))

    assert request["messages"][0]["content"] == "done"


def test_openresponses_tool_result_uses_pydantic_json_text() -> None:
    output = _artifact_output()
    client = OpenResponsesTextClient(
        model=_text_model(Provider.OPENAI),
        provider=Provider.OPENAI,
        auth=AuthHeader(secret=SecretStr("test")),
    )

    request = client._init_request(TextInput(messages=[_tool_result(output)]))

    content = request["input"][0]["output"]
    assert content == output.model_dump_json()
    assert json.loads(content) == output.model_dump(mode="json")


def test_anthropic_tool_result_uses_pydantic_json_text() -> None:
    output = _artifact_output()
    client = AnthropicTextClient(
        model=_text_model(Provider.ANTHROPIC),
        provider=Provider.ANTHROPIC,
        auth=AuthHeader(secret=SecretStr("test"), header="x-api-key", prefix=""),
    )

    request = client._init_request(TextInput(messages=[_tool_result(output)]))

    tool_block = request["messages"][0]["content"][0]
    assert tool_block["content"] == output.model_dump_json()
    assert json.loads(tool_block["content"]) == output.model_dump(mode="json")


def test_google_tool_result_uses_pydantic_json_object() -> None:
    output = _artifact_output()
    client = GoogleTextClient(
        model=_text_model(Provider.GOOGLE),
        provider=Provider.GOOGLE,
        auth=AuthHeader(secret=SecretStr("test"), header="x-goog-api-key", prefix=""),
    )

    request = client._init_request(TextInput(messages=[_tool_result(output)]))

    result = request["contents"][0]["parts"][0]["functionResponse"]["response"][
        "result"
    ]
    assert result == output.model_dump(mode="json")


def test_cohere_message_content_preserves_pydantic_shape() -> None:
    output = _artifact_output()
    client = CohereTextClient(
        model=_text_model(Provider.COHERE),
        provider=Provider.COHERE,
        auth=AuthHeader(secret=SecretStr("test")),
    )

    request = client._init_request(
        TextInput(messages=[Message(role=Role.USER, content=output)])
    )

    assert request["messages"][0]["content"] == output.model_dump(mode="json")
