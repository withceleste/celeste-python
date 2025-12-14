"""Voice definitions for speech generation."""

from pydantic import BaseModel, Field

from celeste import Provider


class Voice(BaseModel):
    """Represents a voice for speech generation."""

    id: str
    provider: Provider
    name: str
    languages: set[str] = Field(default_factory=set)


__all__ = ["Voice"]
