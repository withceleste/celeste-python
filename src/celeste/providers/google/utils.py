"""Shared utilities for Google/Gemini API providers."""

import base64
from typing import Any

import httpx

from celeste.artifacts import Artifact
from celeste.auth import Authentication
from celeste.http import DEFAULT_TIMEOUT, HTTPClient
from celeste.utils import detect_mime_type

from .auth import GoogleADC


async def download_video(
    http_client: HTTPClient,
    auth: Authentication,
    url: str,
    extra_headers: dict[str, str] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> httpx.Response:
    """Download video, authenticating only the matching Google origin on each hop."""
    target = httpx.URL(
        url.replace("gs://", "https://storage.googleapis.com/", 1)
        if url.startswith("gs://")
        else url
    )
    auth_host = (
        "storage.googleapis.com"
        if isinstance(auth, GoogleADC)
        else "generativelanguage.googleapis.com"
    )
    for _ in range(21):
        headers = {}
        if (target.scheme, target.host, target.port) == ("https", auth_host, None):
            headers = {**await auth.aget_headers(), **(extra_headers or {})}
        response = await http_client.get(
            str(target), headers=headers, timeout=timeout, follow_redirects=False
        )
        if response.next_request is None:
            return response
        target = response.next_request.url
    raise httpx.TooManyRedirects(
        "Exceeded maximum allowed redirects.", request=response.request
    )


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


# The Interactions API names MPEG-4 audio "audio/m4a" and hard-rejects "audio/mp4"
# (its own supported-values list; generateContent accepts both, so only this builder maps).
_INTERACTIONS_MIME_LITERALS = {"audio/mp4": "audio/m4a"}


def build_content_part(artifact: Artifact, part_type: str) -> dict[str, Any]:
    """Convert any media artifact to an Interactions API content part."""
    if artifact.url:
        part: dict[str, Any] = {"type": part_type, "uri": artifact.url}
        if artifact.mime_type:
            part["mime_type"] = _interactions_mime(artifact.mime_type.value)
        return part
    media_bytes = artifact.get_bytes()
    b64 = base64.b64encode(media_bytes).decode("utf-8")
    mime = artifact.mime_type or detect_mime_type(media_bytes)
    part = {"type": part_type, "data": b64}
    if mime:
        part["mime_type"] = _interactions_mime(mime.value)
    return part


def _interactions_mime(literal: str) -> str:
    """Translate a celeste mime literal to the Interactions API's vocabulary."""
    return _INTERACTIONS_MIME_LITERALS.get(literal, literal)
