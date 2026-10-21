"""Meta text grounding helpers."""

from typing import Any

from celeste.grounding import Grounding, GroundingSource
from celeste.protocols.openresponses.tools import parse_annotations

from ...grounding import map_url_citation_annotations


def parse_grounding(output: list[dict[str, Any]]) -> Grounding | None:
    """Parse cited spans plus every source Meta's web search calls returned."""
    grounding = map_url_citation_annotations(parse_annotations(output)) or Grounding()
    urls = {source.url for source in grounding.sources}
    for item in output:
        if item.get("type") != "web_search_call":
            continue
        for result in item.get("results") or []:
            url = result.get("url")
            if not isinstance(url, str) or url in urls:
                continue
            urls.add(url)
            title = result.get("title")
            grounding.sources.append(
                GroundingSource(
                    url=url, title=title if isinstance(title, str) else None
                )
            )
    return grounding if grounding.sources else None
