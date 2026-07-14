"""Google text grounding helpers."""

from typing import Any

from celeste.grounding import Citation, Grounding, GroundingSource


def _byte_offset_to_char_offset(text: str, offset: int) -> int | None:
    encoded = text.encode("utf-8")
    if offset < 0 or offset > len(encoded):
        return None
    try:
        return len(encoded[:offset].decode("utf-8"))
    except UnicodeDecodeError:
        return None


def map_grounding(grounding_metadata: dict[str, Any], text: str) -> Grounding:
    """Map Google Gemini groundingMetadata to text grounding."""
    sources: list[GroundingSource] = []
    source_indices: dict[int, int] = {}
    for index, chunk in enumerate(grounding_metadata.get("groundingChunks", [])):
        web = chunk.get("web")
        if not isinstance(web, dict):
            continue
        url = web.get("uri")
        if not isinstance(url, str) or not url:
            continue
        source_indices[index] = len(sources)
        sources.append(
            GroundingSource(
                url=url,
                title=web.get("title"),
                domain=web.get("domain", web.get("title")),
            )
        )

    citations: list[Citation] = []
    for support in grounding_metadata.get("groundingSupports", []):
        segment = support.get("segment", {})
        if not isinstance(segment, dict):
            continue
        start = segment.get("startIndex")
        end = segment.get("endIndex")
        if not isinstance(start, int) or not isinstance(end, int):
            continue
        start = _byte_offset_to_char_offset(text, start)
        end = _byte_offset_to_char_offset(text, end)
        if start is None or end is None:
            continue
        raw_indices = support.get("groundingChunkIndices", [])
        indices = [
            source_indices[i]
            for i in raw_indices
            if isinstance(i, int) and i in source_indices
        ]
        citations.append(
            Citation(
                start=start,
                end=end,
                source_indices=indices,
                cited_text=segment.get("text"),
            )
        )

    entry = grounding_metadata.get("searchEntryPoint") or {}
    return Grounding(
        queries=grounding_metadata.get("webSearchQueries", []),
        sources=sources,
        citations=citations,
        search_entry_point=entry.get("renderedContent"),
    )


__all__ = ["map_grounding"]
