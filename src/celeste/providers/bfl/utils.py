"""Shared BFL artifact utilities."""

from celeste.artifacts import Artifact


def encode_artifact(artifact: Artifact) -> str:
    """Return an artifact URL or raw base64 content for BFL requests."""
    if artifact.url:
        return artifact.url
    return artifact.get_base64()


__all__ = ["encode_artifact"]
