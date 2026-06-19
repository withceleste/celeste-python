"""Anthropic text grounding helpers."""

from typing import Any

from celeste.grounding import Citation, Grounding, GroundingSource


def _source_index(
    sources: list[GroundingSource],
    source_indices: dict[tuple[str, str | None], int],
    url: str,
    title: str | None,
) -> int:
    key = (url, title)
    if key not in source_indices:
        source_indices[key] = len(sources)
        sources.append(GroundingSource(url=url, title=title))
    return source_indices[key]


def parse_grounding(blocks: list[dict[str, Any]]) -> Grounding | None:
    """Parse Anthropic Messages web-search blocks into text grounding."""
    queries: list[str] = []
    sources: list[GroundingSource] = []
    source_indices: dict[tuple[str, str | None], int] = {}
    citations: list[Citation] = []

    for block in blocks:
        if block.get("type") == "server_tool_use" and block.get("name") == "web_search":
            query = block.get("input", {}).get("query")
            if isinstance(query, str):
                queries.append(query)
        if block.get("type") != "web_search_tool_result":
            continue
        content = block.get("content")
        if not isinstance(content, list):
            continue
        for result in content:
            if result.get("type") != "web_search_result":
                continue
            url = result.get("url")
            if isinstance(url, str):
                title = result.get("title")
                _source_index(
                    sources,
                    source_indices,
                    url,
                    title if isinstance(title, str) else None,
                )

    text_pos = 0
    for block in blocks:
        if block.get("type") != "text":
            continue
        block_text = block.get("text")
        if not isinstance(block_text, str) or not block_text:
            continue
        start = text_pos
        end = start + len(block_text)
        text_pos = end
        for raw_citation in block.get("citations", []):
            if raw_citation.get("type") != "web_search_result_location":
                continue
            url = raw_citation.get("url")
            cited_text = raw_citation.get("cited_text")
            if not isinstance(url, str) or not isinstance(cited_text, str):
                continue
            title = raw_citation.get("title")
            idx = _source_index(
                sources,
                source_indices,
                url,
                title if isinstance(title, str) else None,
            )
            citations.append(
                Citation(
                    start=start,
                    end=end,
                    source_indices=[idx],
                    cited_text=cited_text,
                )
            )

    if not queries and not sources and not citations:
        return None
    return Grounding(queries=queries, sources=sources, citations=citations)


__all__ = ["parse_grounding"]
