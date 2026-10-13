"""OpenResponses text joins every message, with citations offset into the joined text."""

from collections.abc import AsyncIterator
from typing import Any

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
