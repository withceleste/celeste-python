"""Text grounding helpers."""

from celeste.grounding import Citation, Grounding, GroundingSource


def map_url_citation_annotations(
    annotations: list[dict[str, object]],
) -> Grounding | None:
    """Map native URL citation annotations into text grounding."""
    sources: list[GroundingSource] = []
    source_indices: dict[tuple[str, str | None], int] = {}
    citations: list[Citation] = []

    for annotation in annotations:
        if annotation.get("type") != "url_citation":
            continue
        nested = annotation.get("url_citation")
        citation: dict[str, object] = nested if isinstance(nested, dict) else annotation
        url = citation.get("url")
        start = citation.get("start_index")
        end = citation.get("end_index")
        if (
            not isinstance(url, str)
            or not isinstance(start, int)
            or not isinstance(end, int)
        ):
            continue
        raw_title = citation.get("title")
        title = (
            raw_title
            if isinstance(raw_title, str) and not raw_title.strip().isdigit()
            else None
        )
        key = (url, title)
        if key not in source_indices:
            source_indices[key] = len(sources)
            sources.append(GroundingSource(url=url, title=key[1]))
        citations.append(
            Citation(
                start=start,
                end=end,
                source_indices=[source_indices[key]],
            )
        )

    return Grounding(sources=sources, citations=citations) if citations else None


__all__ = ["map_url_citation_annotations"]
