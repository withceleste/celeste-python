"""Web-search grounding for generated responses."""

from pydantic import BaseModel, Field


class GroundingSource(BaseModel):
    """A web source the response was grounded in."""

    url: str
    title: str | None = None
    domain: str | None = None


class Citation(BaseModel):
    """Links a span of the response text to its sources."""

    start: int
    end: int
    source_indices: list[int] = Field(default_factory=list)
    cited_text: str | None = None


class Grounding(BaseModel):
    """Web-search grounding: queries, sources, and per-span citations."""

    queries: list[str] = Field(default_factory=list)
    sources: list[GroundingSource] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    search_entry_point: str | None = None


__all__ = ["Citation", "Grounding", "GroundingSource"]
