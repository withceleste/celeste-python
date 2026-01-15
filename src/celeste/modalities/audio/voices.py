"""Voice definitions for speech generation."""

from pydantic import BaseModel, Field

from celeste.core import Provider

from .languages import Language


class Voice(BaseModel):
    """Represents a voice for speech generation."""

    id: str
    provider: Provider
    name: str
    languages: set[Language] = Field(default_factory=set)


__all__ = ["Voice"]
