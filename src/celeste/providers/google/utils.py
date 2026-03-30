"""Shared utilities for Google/Gemini API providers."""

import base64
from typing import Any

from celeste.artifacts import Artifact
from celeste.utils import detect_mime_type


def build_media_part(artifact: Artifact) -> dict[str, Any]:
    """Convert any media artifact to a Gemini inline_data/file_data part."""
    if artifact.url:
        part: dict[str, Any] = {"file_data": {"file_uri": artifact.url}}
        if artifact.mime_type:
            part["file_data"]["mime_type"] = artifact.mime_type.value
        return part
    media_bytes = artifact.get_bytes()
    b64 = base64.b64encode(media_bytes).decode("utf-8")
    mime = artifact.mime_type or detect_mime_type(media_bytes)
    mime_str = mime.value if mime else None
    return {"inline_data": {"mime_type": mime_str, "data": b64}}
