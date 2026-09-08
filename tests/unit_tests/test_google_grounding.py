"""Google grounding uses Part-relative UTF-8 offsets, not output offsets."""

from collections.abc import AsyncIterator
from typing import Any

import pytest

from celeste.modalities.text.providers.google.grounding import map_grounding_vertex
from celeste.modalities.text.providers.google.vertex import (
    GoogleVertexTextClient,
    GoogleVertexTextStream,
)

PARTS = [
    {"text": "secret", "thought": True},
    {"text": "Café "},
    {"executableCode": {"language": "PYTHON", "code": "1 + 1"}},
    {"text": "🫖 éclair"},
]
SOURCE = {"web": {"uri": "https://example.test/source"}}
SEGMENT = {"partIndex": 3, "startIndex": 5, "endIndex": 12, "text": "éclair"}


async def _events(
    groups: list[list[dict[str, Any]]], meta: dict
) -> AsyncIterator[dict]:
    for group in groups:
        yield {"candidates": [{"content": {"parts": group}}]}
    yield {
        "candidates": [
            {"finishReason": "STOP", "groundingMetadata": meta},
            {"groundingMetadata": {"groundingChunks": [SOURCE]}},
        ]
    }


@pytest.mark.parametrize("bundled", [True, False])
async def test_grounding_preserves_part_boundaries_and_native_replay(
    bundled: bool,
) -> None:
    meta = {
        "groundingChunks": [SOURCE],
        "groundingSupports": [
            {"segment": SEGMENT, "groundingChunkIndices": [0]},
            {"segment": {"partIndex": 1, "endIndex": 5, "text": "Café"}},
        ],
    }
    response = {
        "candidates": [{"content": {"parts": PARTS}, "groundingMetadata": meta}]
    }
    client = object.__new__(GoogleVertexTextClient)
    grounding = client._parse_grounding(response)
    assert grounding is not None
    assert [(c.start, c.end) for c in grounding.citations] == [(7, 13), (0, 4)]
    assert grounding.citations[0].source_indices == [0]
    groups = (
        [PARTS]
        if bundled
        else [[{"text": text, "thought": True}] for text in ("sec", "ret")]
        + [[{"text": "Ca"}], [{"text": "fé "}], [PARTS[2]]]
        + [[{"text": text}] for text in ("🫖 ", "écl", "air")]
    )
    stream = GoogleVertexTextStream(_events(groups, meta))
    _ = [chunk async for chunk in stream]
    assert stream.output.content == client._parse_content(response) == "Café 🫖 éclair"
    assert stream.output.grounding == grounding
    assert stream.output.signature == [part for group in groups for part in group]


@pytest.mark.parametrize(
    "invalid",
    [{"partIndex": index} for index in (-1, 0, 2, 99, "bad")]
    + [{"startIndex": 1}, {"endIndex": 99}, {"startIndex": 13}, {"text": "wrong"}],
)
def test_grounding_omits_invalid_spans_without_losing_sources(invalid: dict) -> None:
    result = map_grounding_vertex(
        {
            "groundingChunks": [SOURCE],
            "groundingSupports": [{"segment": SEGMENT | invalid}],
        },
        PARTS,
    )
    assert result.citations == []
    assert result.sources[0].url == SOURCE["web"]["uri"]


@pytest.mark.parametrize("bundled", [True, False])
async def test_grounding_metadata_only_terminal_keeps_text_part_offsets(
    bundled: bool,
) -> None:
    parts = [{"text": "Alpha "}, {"text": "Beta"}]
    segment = (
        {"partIndex": 1, "endIndex": 4, "text": "Beta"}
        if bundled
        else {"endIndex": 10, "text": "Alpha Beta"}
    )
    meta = {"groundingSupports": [{"segment": segment}]}
    groups = [parts] if bundled else [[part] for part in parts]
    stream = GoogleVertexTextStream(_events(groups, meta))
    _ = [chunk async for chunk in stream]
    assert stream.output.grounding is not None
    citation = stream.output.grounding.citations[0]
    assert stream.output.content == "Alpha Beta"
    assert (citation.start, citation.end) == ((6, 10) if bundled else (0, 10))
