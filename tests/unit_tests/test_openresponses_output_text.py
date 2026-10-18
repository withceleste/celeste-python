"""OpenResponses text joins every message, with citations offset into the joined text."""

from collections.abc import AsyncIterator
from copy import deepcopy
from typing import Any

import pytest
from pydantic import BaseModel

from celeste import Model, NoAuth, Protocol
from celeste.modalities.text.parameters import TextParameters
from celeste.modalities.text.protocols.openresponses.client import (
    OpenResponsesTextClient,
    OpenResponsesTextStream,
)

COMMENTARY = "I'll search. "
ANSWER = "Python 3.12 shipped on October 2, 2023."
CITATION = {
    "type": "url_citation",
    "url": "https://docs.python.org/3.12/whatsnew/3.12.html",
    "title": "What's New In Python 3.12",
    "start_index": 0,
    "end_index": 11,
}
OUTPUT = [
    {
        "type": "message",
        "phase": "commentary",
        "content": [{"type": "output_text", "text": COMMENTARY, "annotations": []}],
    },
    {"type": "web_search_call", "status": "completed"},
    {
        "type": "message",
        "phase": "final_answer",
        "content": [{"type": "output_text", "text": ANSWER, "annotations": [CITATION]}],
    },
]
RESPONSE: dict[str, Any] = {"status": "completed", "output": OUTPUT}


async def _events() -> AsyncIterator[dict[str, Any]]:
    for text in (COMMENTARY, ANSWER):
        yield {"type": "response.output_text.delta", "delta": text}
    yield {"type": "response.completed", "response": RESPONSE}


async def test_unary_and_stream_join_every_message_with_shifted_citations() -> None:
    client = object.__new__(OpenResponsesTextClient)
    stream = OpenResponsesTextStream(_events())
    _ = [chunk async for chunk in stream]

    content = client._parse_content(RESPONSE)
    grounding = client._parse_grounding(RESPONSE)
    assert stream.output.content == content == COMMENTARY + ANSWER
    assert stream.output.grounding == grounding
    assert grounding is not None
    citation = grounding.citations[0]
    assert content[citation.start : citation.end] == "Python 3.12"


class RefusalAnswer(BaseModel):
    value: int


def _refusal_client() -> OpenResponsesTextClient:
    return OpenResponsesTextClient(
        model=Model(id="refusal-test", display_name="Refusal test", streaming=True),
        protocol=Protocol.OPENRESPONSES,
        auth=NoAuth(),
        base_url=None,
    )


@pytest.mark.parametrize("output_schema", [None, RefusalAnswer])
async def test_refusal_metadata_survives_unary_and_stream_output(
    monkeypatch: pytest.MonkeyPatch,
    output_schema: type[BaseModel] | None,
) -> None:
    message = {
        "type": "message",
        "id": "msg-1",
        "role": "assistant",
        "status": "completed",
        "content": [{"type": "refusal", "refusal": "Unable to provide that."}],
    }
    response = {
        "status": "completed",
        "output": [message],
        "usage": {"input_tokens": 1, "output_tokens": 2, "total_tokens": 3},
    }
    original = deepcopy(response)

    async def make_request(*_args: object, **_kwargs: object) -> dict[str, Any]:
        return response

    async def events() -> AsyncIterator[dict[str, Any]]:
        yield {"type": "response.completed", "response": response}

    async def make_stream_request(
        *_args: object, **_kwargs: object
    ) -> AsyncIterator[dict[str, Any]]:
        return events()

    client = _refusal_client()
    monkeypatch.setattr(type(client), "_make_request", make_request)
    monkeypatch.setattr(type(client), "_make_stream_request", make_stream_request)
    parameters: TextParameters = {}
    if output_schema is not None:
        parameters["output_schema"] = output_schema
    output = await client.generate("Test refusal", **parameters)
    stream = client.stream.generate("Test refusal", **parameters)
    _ = [chunk async for chunk in stream]

    assert output.finish_reason is not None
    assert stream.output.finish_reason is not None
    assert output.content == stream.output.content == ""
    assert (
        output.finish_reason.reason == stream.output.finish_reason.reason == "completed"
    )
    assert output.usage.total_tokens == stream.output.usage.total_tokens == 3
    assert output.metadata["raw_response"]["output"] == [message]
    assert stream.output.metadata["raw_response"]["output"] == [message]
    assert response == original


@pytest.mark.parametrize("refusal_text", ["Unable to provide that.", ""])
def test_metadata_preserves_refusals_and_billing_markers_in_output_order(
    refusal_text: str,
) -> None:
    refusal = {"type": "refusal", "refusal": refusal_text}
    text = {"type": "output_text", "text": "Ordinary answer", "annotations": []}
    message = {
        "type": "message",
        "id": "msg-1",
        "role": "assistant",
        "status": "completed",
        "phase": "final_answer",
        "content": [text, refusal],
    }
    second_message = {**message, "id": "msg-2", "content": [refusal]}
    response = {
        "status": "completed",
        "output": [
            {
                "type": "web_search_call",
                "status": "completed",
                "action": {"query": "q"},
            },
            message,
            {**message, "id": "text-only", "content": [text]},
            {"type": "file_search_call", "status": "completed", "results": ["file"]},
            second_message,
        ],
    }
    original = deepcopy(response)

    metadata = _refusal_client()._build_metadata(response)

    assert metadata["raw_response"]["output"] == [
        {"type": "web_search_call", "status": "completed"},
        {**message, "content": [refusal]},
        {"type": "file_search_call", "status": "completed"},
        second_message,
    ]
    assert response == original


def test_metadata_excludes_text_only_output() -> None:
    response = {"output": [OUTPUT[0], OUTPUT[-1]]}
    assert "output" not in _refusal_client()._build_metadata(response)["raw_response"]
