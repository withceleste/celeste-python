"""Groq text grounding helpers."""

from typing import Any

from celeste.grounding import Grounding, GroundingSource
from celeste.providers.groq.chat.tools import parse_search_results


def parse_grounding(executed_tools: Any) -> Grounding | None:  # noqa: ANN401
    """Parse Groq executed_tools search results into text grounding."""
    sources: list[GroundingSource] = []
    seen: set[tuple[str, str | None]] = set()
    for result in parse_search_results(executed_tools):
        url = result.get("url")
        if not isinstance(url, str):
            continue
        title = result.get("title")
        key = (url, title if isinstance(title, str) else None)
        if key in seen:
            continue
        seen.add(key)
        sources.append(GroundingSource(url=url, title=key[1]))

    return Grounding(sources=sources) if sources else None
