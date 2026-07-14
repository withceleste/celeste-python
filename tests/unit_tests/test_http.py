from collections.abc import AsyncIterator, Generator
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock, call, patch

import httpx
import pytest

import celeste.http as http_module
from celeste.core import Modality, Provider
from celeste.http import (
    DEFAULT_TIMEOUT,
    MAX_RETRIES,
    HTTPClient,
    clear_http_clients,
    close_all_http_clients,
    get_http_client,
)


@pytest.fixture
def transport() -> AsyncMock:
    client = AsyncMock(spec=httpx.AsyncClient)
    client.post = AsyncMock(return_value=httpx.Response(200))
    client.get = AsyncMock(return_value=httpx.Response(200))
    client.aclose = AsyncMock()
    return client


@pytest.fixture(autouse=True)
def isolated_registry() -> Generator[None]:
    previous = http_module._http_clients.copy()
    http_module._http_clients.clear()
    yield
    http_module._http_clients.clear()
    http_module._http_clients.update(previous)


async def test_client_is_lazy_reused_and_closed(transport: AsyncMock) -> None:
    client = HTTPClient(max_connections=7, max_keepalive_connections=3)
    assert client._client is None

    with patch("celeste.http.httpx.AsyncClient", return_value=transport) as constructor:
        await client.post("https://example.com/one", {}, {})
        await client.post("https://example.com/two", {}, {})
        created = client._client
        await client.aclose()

    assert constructor.call_count == 1
    limits = constructor.call_args.kwargs["limits"]
    assert (limits.max_connections, limits.max_keepalive_connections) == (7, 3)
    assert created is transport
    assert client._client is None
    transport.aclose.assert_awaited_once()


@pytest.mark.parametrize("operation", ["post", "post_multipart", "get"])
async def test_request_methods_forward_arguments(
    operation: str, transport: AsyncMock
) -> None:
    client = HTTPClient()
    with patch("celeste.http.httpx.AsyncClient", return_value=transport):
        if operation == "post":
            await client.post(
                "https://example.com",
                {"Authorization": "key"},
                {"prompt": "hello"},
                timeout=10,
            )
            assert transport.post.call_args == call(
                "https://example.com",
                headers={"Authorization": "key"},
                json={"prompt": "hello"},
                timeout=10,
            )
        elif operation == "post_multipart":
            await client.post_multipart(
                "https://example.com",
                {"Authorization": "key"},
                {"file": ("input.bin", b"data", "application/octet-stream")},
                {"purpose": "input"},
            )
            assert transport.post.call_args == call(
                "https://example.com",
                headers={"Authorization": "key"},
                files={"file": ("input.bin", b"data", "application/octet-stream")},
                data={"purpose": "input"},
                timeout=DEFAULT_TIMEOUT,
            )
        else:
            await client.get(
                "https://example.com", {"Authorization": "key"}, timeout=12
            )
            assert transport.get.call_args == call(
                "https://example.com",
                headers={"Authorization": "key"},
                timeout=12,
                follow_redirects=True,
            )


@pytest.mark.parametrize(
    ("operation", "arguments"),
    [
        ("post", {"headers": {}, "json_body": {}}),
        ("post_multipart", {"headers": {}, "files": {}, "data": {}}),
        ("get", {}),
    ],
)
async def test_request_methods_reject_blank_urls(
    operation: str, arguments: dict[str, Any]
) -> None:
    with pytest.raises(ValueError, match="URL cannot be empty"):
        await getattr(HTTPClient(), operation)(" ", **arguments)


@pytest.mark.parametrize(
    ("outcomes", "status", "calls"),
    [
        ([httpx.ReadTimeout("timeout"), httpx.Response(200)], 200, 2),
        ([httpx.Response(503), httpx.Response(200)], 200, 2),
        ([httpx.Response(401)], 401, 1),
        ([httpx.Response(503)] * (MAX_RETRIES + 1), 503, MAX_RETRIES + 1),
    ],
)
async def test_retry_policy(
    transport: AsyncMock,
    outcomes: list[object],
    status: int,
    calls: int,
) -> None:
    transport.post.side_effect = outcomes
    with (
        patch("celeste.http.httpx.AsyncClient", return_value=transport),
        patch("celeste.http.asyncio.sleep", new=AsyncMock()),
    ):
        response = await HTTPClient().post("https://example.com", {}, {})
    assert response.status_code == status
    assert transport.post.call_count == calls


async def test_retry_exhaustion_reraises_transport_error(
    transport: AsyncMock,
) -> None:
    transport.post.side_effect = httpx.ConnectError("down")
    with (
        patch("celeste.http.httpx.AsyncClient", return_value=transport),
        patch("celeste.http.asyncio.sleep", new=AsyncMock()),
        pytest.raises(httpx.ConnectError, match="down"),
    ):
        await HTTPClient().post("https://example.com", {}, {})
    assert transport.post.call_count == MAX_RETRIES + 1


def test_registry_is_keyed_by_provider_and_modality() -> None:
    openai_text = get_http_client(Provider.OPENAI, Modality.TEXT)
    assert get_http_client(Provider.OPENAI, Modality.TEXT) is openai_text
    assert get_http_client(Provider.OPENAI, Modality.IMAGES) is not openai_text
    assert get_http_client(Provider.ANTHROPIC, Modality.TEXT) is not openai_text


async def test_close_all_continues_after_a_client_failure() -> None:
    failing = get_http_client(Provider.OPENAI, Modality.TEXT)
    healthy = get_http_client(Provider.ANTHROPIC, Modality.TEXT)
    failing_transport = AsyncMock(spec=httpx.AsyncClient)
    healthy_transport = AsyncMock(spec=httpx.AsyncClient)
    failing_transport.aclose.side_effect = RuntimeError("close failed")
    failing._client = failing_transport
    healthy._client = healthy_transport

    await close_all_http_clients()

    failing_transport.aclose.assert_awaited_once()
    healthy_transport.aclose.assert_awaited_once()
    assert not http_module._http_clients


def test_clear_registry_does_not_close_clients() -> None:
    client = get_http_client(Provider.OPENAI, Modality.TEXT)
    client._client = AsyncMock(spec=httpx.AsyncClient)
    clear_http_clients()
    client._client.aclose.assert_not_called()
    assert not http_module._http_clients


async def test_context_manager_closes_on_exception(transport: AsyncMock) -> None:
    client = HTTPClient()
    with (
        patch("celeste.http.httpx.AsyncClient", return_value=transport),
        pytest.raises(RuntimeError, match="boom"),
    ):
        async with client as entered:
            assert entered is client
            await client.post("https://example.com", {}, {})
            raise RuntimeError("boom")
    assert client._client is None
    transport.aclose.assert_awaited_once()


async def _iterate(items: list[Any]) -> AsyncIterator[Any]:
    for item in items:
        yield item


def _event_source(data: list[str], response: httpx.Response | None = None) -> MagicMock:
    source = MagicMock()
    source.response = response or httpx.Response(
        200, request=httpx.Request("POST", "https://example.com")
    )
    source.aiter_sse.return_value = _iterate(
        [SimpleNamespace(data=item) for item in data]
    )
    source.__aenter__ = AsyncMock(return_value=source)
    source.__aexit__ = AsyncMock(return_value=False)
    return source


async def test_sse_stream_forwards_arguments_and_skips_control_messages(
    transport: AsyncMock,
) -> None:
    source = _event_source(['{"delta": "hello"}', "[DONE]", '{"delta": "!"}'])
    with (
        patch("celeste.http.httpx.AsyncClient", return_value=transport),
        patch("celeste.http.aconnect_sse", return_value=source) as connect,
    ):
        events = [
            event
            async for event in HTTPClient().stream_post(
                "https://example.com",
                {"Authorization": "key"},
                {"stream": True},
                timeout=10,
            )
        ]

    assert events == [{"delta": "hello"}, {"delta": "!"}]
    connect.assert_called_once_with(
        transport,
        "POST",
        "https://example.com",
        json={"stream": True},
        headers={"Authorization": "key"},
        timeout=10,
    )


async def test_sse_error_body_remains_readable(transport: AsyncMock) -> None:
    response = httpx.Response(
        401,
        content=b'{"error": {"message": "invalid key"}}',
        request=httpx.Request("POST", "https://example.com"),
    )
    with (
        patch("celeste.http.httpx.AsyncClient", return_value=transport),
        patch("celeste.http.aconnect_sse", return_value=_event_source([], response)),
        pytest.raises(httpx.HTTPStatusError) as error,
    ):
        async for _ in HTTPClient().stream_post("https://example.com", {}, {}):
            pass
    assert error.value.response.json()["error"]["message"] == "invalid key"


class AsyncResponseContext:
    def __init__(self, response: httpx.Response) -> None:
        self.response = response

    async def __aenter__(self) -> httpx.Response:
        return self.response

    async def __aexit__(self, *_args: object) -> None:
        return None


async def test_ndjson_stream_parses_nonempty_lines(transport: AsyncMock) -> None:
    response = httpx.Response(
        200,
        content=b'{"value": 1}\n\n{"value": 2}\n',
        request=httpx.Request("POST", "https://example.com"),
    )
    transport.stream = MagicMock(return_value=AsyncResponseContext(response))
    with patch("celeste.http.httpx.AsyncClient", return_value=transport):
        events = [
            event
            async for event in HTTPClient().stream_post_ndjson(
                "https://example.com", {}, {}
            )
        ]
    assert events == [{"value": 1}, {"value": 2}]


async def test_ndjson_error_body_remains_readable(transport: AsyncMock) -> None:
    response = httpx.Response(
        403,
        content=b'{"error": {"message": "forbidden"}}',
        request=httpx.Request("POST", "https://example.com"),
    )
    transport.stream = MagicMock(return_value=AsyncResponseContext(response))
    with (
        patch("celeste.http.httpx.AsyncClient", return_value=transport),
        pytest.raises(httpx.HTTPStatusError) as error,
    ):
        async for _ in HTTPClient().stream_post_ndjson("https://example.com", {}, {}):
            pass
    assert error.value.response.json()["error"]["message"] == "forbidden"
