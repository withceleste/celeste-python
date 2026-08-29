"""Shared utilities for Google/Gemini API providers."""

import base64
from typing import Any
from urllib.parse import urljoin, urlsplit

import httpx

from celeste.artifacts import Artifact
from celeste.http import HTTPClient
from celeste.utils import detect_mime_type

_MAX_REDIRECTS = 20
_AUTHENTICATED_DOWNLOAD_HOSTS = frozenset(
    {"generativelanguage.googleapis.com", "storage.googleapis.com"}
)


async def get_with_auth_safe_redirects(
    client: HTTPClient,
    url: str,
    headers: dict[str, str],
    *,
    timeout: float,
) -> httpx.Response:
    """Follow GET redirects without forwarding credentials across origins."""
    current_url = url
    parsed = urlsplit(current_url)
    current_headers = (
        headers
        if parsed.scheme == "https" and parsed.hostname in _AUTHENTICATED_DOWNLOAD_HOSTS
        else {}
    )
    for _ in range(_MAX_REDIRECTS):
        response = await client.get(
            current_url,
            headers=current_headers,
            timeout=timeout,
            follow_redirects=False,
        )
        if not response.is_redirect or "location" not in response.headers:
            return response
        redirect_url = urljoin(current_url, response.headers["location"])
        if urlsplit(redirect_url)[:2] != urlsplit(current_url)[:2]:
            current_headers = {}
        current_url = redirect_url
    raise httpx.TooManyRedirects(
        "Exceeded maximum allowed redirects", request=response.request
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
