"""Google download credential isolation and asynchronous ADC."""

import asyncio
import threading
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import httpx
import pytest

from celeste import Modality, Provider, create_client
from celeste.artifacts import VideoArtifact
from celeste.auth import AuthHeader
from celeste.providers.google.auth import GoogleADC

from ._http_helpers import _mock_http, _sse


@pytest.mark.parametrize(
    "model", ["veo-3.1-generate-preview", "gemini-omni-flash-preview"]
)
@pytest.mark.parametrize("adc", [False, True])
async def test_google_download_auth_is_scoped_to_each_hops_origin(
    model: str, adc: bool
) -> None:
    credentials = (
        {"Authorization": "Bearer test", "x-goog-user-project": "test-project"}
        if adc
        else {"x-goog-api-key": "test"}
    )
    auth = (
        GoogleADC(project_id="test-project")
        if adc
        else AuthHeader(secret="test", header="x-goog-api-key", prefix="")  # nosec B106
    )
    host = "storage.googleapis.com" if adc else "generativelanguage.googleapis.com"
    seen: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.url.path == "/start":
            return httpx.Response(302, headers={"location": "/same-origin"})
        if request.url.path == "/same-origin":
            return httpx.Response(
                302, headers={"location": "https://external.test/final"}
            )
        return httpx.Response(200, content=b"video")

    client = create_client(
        modality=Modality.VIDEOS, provider=Provider.GOOGLE, model=model, auth=auth
    )
    async with _mock_http(handle):
        with patch.object(GoogleADC, "get_headers", return_value=credentials):
            for url in (
                f"http://{host}/file",
                f"https://{host}:8443/file",
                f"https://{host}.external.test/file",
                "https://external.test/file",
            ):
                result = await client.download_content(VideoArtifact(url=url))
                assert result.data == b"video"
                assert all(key not in seen[-1].headers for key in credentials)
            seen.clear()
            url = "gs://start" if adc else f"https://{host}/start"
            await client.download_content(VideoArtifact(url=url))
            assert len(seen) == 3
            for request in seen[:2]:
                assert all(
                    request.headers[key] == value for key, value in credentials.items()
                )
            assert all(key not in seen[-1].headers for key in credentials)


async def test_adc_discovery_and_refresh_are_offloaded_and_shared() -> None:
    google_auth = pytest.importorskip("google.auth")
    auth = GoogleADC()
    loop = asyncio.get_running_loop()
    entered = asyncio.Event()
    release = threading.Event()
    threads: list[int] = []
    credentials = SimpleNamespace(valid=False, token="test")  # nosec B106

    def refresh(_: object) -> None:
        threads.append(threading.get_ident())
        loop.call_soon_threadsafe(entered.set)
        assert release.wait(5)
        credentials.valid = True

    credentials.refresh = refresh

    def discover(**_: object) -> tuple[Any, str]:
        threads.append(threading.get_ident())
        return credentials, "test-project"

    text = create_client(
        modality=Modality.TEXT,
        provider=Provider.GOOGLE,
        model="gemini-2.5-flash",
        auth=auth,
    )
    embeddings = create_client(
        modality=Modality.EMBEDDINGS, provider=Provider.GOOGLE, auth=auth
    )
    payload = {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}

    def handle(request: httpx.Request) -> httpx.Response:
        assert "/projects/test-project/" in request.url.path
        if "streamGenerateContent" in request.url.path:
            return _sse(payload)
        if "embedContent" in request.url.path:
            return httpx.Response(200, json={"embedding": {"values": [0.1]}})
        return httpx.Response(200, json=payload)

    async def consume() -> str:
        stream = text.stream.generate("hello")
        _ = [chunk async for chunk in stream]
        return stream.output.content

    async with _mock_http(handle):
        with patch.object(google_auth, "default", discover):
            tasks = [
                asyncio.create_task(text.generate("hello")),
                asyncio.create_task(consume()),
                asyncio.create_task(embeddings.embed(text=["a", "b"])),
            ]
            try:
                await asyncio.wait_for(entered.wait(), 2)
                assert all(thread != threading.get_ident() for thread in threads)
            finally:
                release.set()
            unary, streamed, vectors = await asyncio.gather(*tasks)
    assert unary.content == streamed == "ok"
    assert len(vectors.content) == 2
    assert len(threads) == 2  # One discovery and one refresh across concurrent calls.
