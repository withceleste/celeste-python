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


def map_grounding_vertex(
    grounding_metadata: dict[str, Any], parts: list[dict[str, Any]]
) -> Grounding:
    """Map generateContent groundingMetadata to text grounding."""
    text_parts: list[tuple[str | None, int]] = []
    offset = 0
    for part in parts:
        text = part.get("text") if not part.get("thought") else None
        text_parts.append((text, offset))
        if isinstance(text, str):
            offset += len(text)

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
        part_index = segment.get("partIndex", 0)
        if not isinstance(part_index, int) or not 0 <= part_index < len(text_parts):
            continue
        text, offset = text_parts[part_index]
        if not isinstance(text, str):
            continue
        start = segment.get("startIndex", 0)
        end = segment.get("endIndex")
        if not isinstance(start, int) or not isinstance(end, int):
            continue
        start = _byte_offset_to_char_offset(text, start)
        end = _byte_offset_to_char_offset(text, end)
        if start is None or end is None or start > end:
            continue
        cited_text = segment.get("text")
        if isinstance(cited_text, str) and text[start:end] != cited_text:
            continue
        raw_indices = support.get("groundingChunkIndices", [])
        indices = [
            source_indices[i]
            for i in raw_indices
            if isinstance(i, int) and i in source_indices
        ]
        citations.append(
            Citation(
                start=offset + start,
                end=offset + end,
                source_indices=indices,
                cited_text=cited_text,
            )
        )

    entry = grounding_metadata.get("searchEntryPoint") or {}
    return Grounding(
        queries=grounding_metadata.get("webSearchQueries", []),
        sources=sources,
        citations=citations,
        search_entry_point=entry.get("renderedContent"),
    )


def map_grounding_interactions(steps: list[dict[str, Any]]) -> Grounding | None:
    """Map Interactions API google_search steps and text annotations to grounding."""
    queries: list[str] = []
    search_entry_point: str | None = None
    for step in steps:
        step_type = step.get("type")
        if step_type == "google_search_call":
            queries.extend(step.get("arguments", {}).get("queries", []))
        elif step_type == "google_search_result":
            for item in step.get("result", []):
                suggestions = item.get("search_suggestions")
                if suggestions:
                    search_entry_point = suggestions

    sources: list[GroundingSource] = []
    source_indices: dict[str, int] = {}
    citations: list[Citation] = []
    for step in steps:
        if step.get("type") != "model_output":
            continue
        for part in step.get("content", []):
            if part.get("type") != "text":
                continue
            part_text = part.get("text", "")
            for annotation in part.get("annotations", []):
                if annotation.get("type") != "url_citation":
                    continue
                url = annotation.get("url")
                if not isinstance(url, str) or not url:
                    continue
                if url not in source_indices:
                    source_indices[url] = len(sources)
                    title = annotation.get("title")
                    sources.append(
                        GroundingSource(
                            url=url,
                            title=title,
                            domain=annotation.get("domain") or title,
                        )
                    )
                start = annotation.get("start_index")
                end = annotation.get("end_index")
                if not isinstance(start, int) or not isinstance(end, int):
                    continue
                start = _byte_offset_to_char_offset(part_text, start)
                end = _byte_offset_to_char_offset(part_text, end)
                if start is None or end is None:
                    continue
                citations.append(
                    Citation(
                        start=start,
                        end=end,
                        source_indices=[source_indices[url]],
                        cited_text=part_text[start:end] or None,
                    )
                )

    if not queries and not sources and not citations:
        return None

    return Grounding(
        queries=queries,
        sources=sources,
        citations=citations,
        search_entry_point=search_entry_point,
    )


__all__ = ["map_grounding_interactions", "map_grounding_vertex"]
