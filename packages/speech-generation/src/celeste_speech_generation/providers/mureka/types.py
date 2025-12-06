"""Mureka-specific types for speech generation."""

from pydantic import BaseModel


class PodcastTurn(BaseModel):
    """A single turn in a podcast conversation."""

    text: str
    voice: str  # One of the Mureka voices (Ethan, Victoria, Jake, Luna, Emma)


class PodcastOutput(BaseModel):
    """Output for podcast generation."""

    url: str
    expires_at: int  # Unix timestamp in seconds


__all__ = [
    "PodcastOutput",
    "PodcastTurn",
]
