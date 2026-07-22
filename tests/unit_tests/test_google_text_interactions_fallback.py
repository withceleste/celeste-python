"""Regression coverage for Google's temporary mixed-tool fallback."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import SecretStr

from celeste import Model
from celeste.auth import AuthHeader
from celeste.core import Provider
from celeste.modalities.text.io import TextInput, TextOutput
from celeste.modalities.text.providers.google.client import GoogleTextClient
from celeste.modalities.text.providers.google.interactions import (
    GoogleInteractionsTextClient,
)
from celeste.modalities.text.providers.google.vertex import (
    GoogleVertexTextClient,
    GoogleVertexTextStream,
)
from celeste.modalities.text.streaming import TextStream
from celeste.providers.google.auth import GoogleADC
from celeste.tools import ToolChoice, ToolDefinition, WebSearch

_FUNCTION_TOOL: dict[str, Any] = {
    "name": "record_result",
    "parameters": {"type": "object"},
}
_MIXED_TOOLS: list[ToolDefinition] = [WebSearch(), _FUNCTION_TOOL]


def _client(
    model_id: str,
    auth: AuthHeader | GoogleADC | None = None,
) -> GoogleTextClient:
    return GoogleTextClient(
        model=Model(id=model_id, provider=Provider.GOOGLE, display_name=model_id),
        provider=Provider.GOOGLE,
        auth=auth
        or AuthHeader(secret=SecretStr("test"), header="x-goog-api-key", prefix=""),
    )


@pytest.mark.parametrize("model_id", ["gemini-3.5-flash-lite", "gemini-3.6-flash"])
def test_affected_mixed_requests_select_generate_content(model_id: str) -> None:
    fallback = _client(model_id)._generate_content_fallback(_MIXED_TOOLS)

    assert isinstance(fallback, GoogleVertexTextClient)
    request = fallback._build_request(
        TextInput(prompt="Search, then record the result."),
        tools=_MIXED_TOOLS,
        tool_choice=ToolChoice.AUTO,
    )
    assert request["toolConfig"] == {
        "includeServerSideToolInvocations": True,
        "functionCallingConfig": {"mode": "AUTO"},
    }


@pytest.mark.parametrize(
    ("model_id", "tools"),
    [
        ("gemini-3.6-flash", [WebSearch()]),
        ("gemini-3.6-flash", [_FUNCTION_TOOL]),
        ("gemini-3.5-flash", _MIXED_TOOLS),
    ],
)
def test_other_requests_stay_on_interactions(
    model_id: str, tools: list[ToolDefinition]
) -> None:
    client = _client(model_id)

    assert isinstance(client._strategy, GoogleInteractionsTextClient)
    assert client._generate_content_fallback(tools) is None


def test_adc_needs_no_fallback() -> None:
    client = _client("gemini-3.6-flash", GoogleADC(project_id="test"))

    assert isinstance(client._strategy, GoogleVertexTextClient)
    assert client._generate_content_fallback(_MIXED_TOOLS) is None


@pytest.mark.asyncio
async def test_unary_request_delegates_to_generate_content(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = TextOutput(content="ok")
    predict = AsyncMock(return_value=expected)
    monkeypatch.setattr(GoogleVertexTextClient, "_predict", predict)

    output = await _client("gemini-3.6-flash").generate(
        "Search, then record the result.", tools=_MIXED_TOOLS
    )

    assert output is expected
    predict.assert_awaited_once()


def test_stream_request_uses_generate_content_stream(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = MagicMock(spec=TextStream)
    stream = MagicMock(return_value=expected)
    monkeypatch.setattr(GoogleVertexTextClient, "_stream", stream)

    output = _client("gemini-3.6-flash").stream.generate(
        "Search, then record the result.", tools=_MIXED_TOOLS
    )

    assert output is expected
    assert stream.call_args.args[1] is GoogleVertexTextStream
