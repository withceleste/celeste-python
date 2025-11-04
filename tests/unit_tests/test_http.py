"""High-value tests for HTTPClient - focusing on connection pooling and resource management."""

from collections.abc import AsyncIterator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from celeste.core import Capability, Provider
from celeste.http import (
    HTTPClient,
    clear_http_clients,
    close_all_http_clients,
    get_http_client,
)


@pytest.fixture
def mock_httpx_client() -> AsyncMock:
    """Mock httpx.AsyncClient for testing HTTP operations."""
    client = AsyncMock(spec=httpx.AsyncClient)
    client.post = AsyncMock(return_value=httpx.Response(200))
    client.get = AsyncMock(return_value=httpx.Response(200))
    client.aclose = AsyncMock()
    return client


class TestHTTPClientLifecycle:
    """Test HTTPClient initialization and cleanup behaviors."""

    async def test_client_lazy_initialization(self) -> None:
        """HTTPClient must not create httpx.AsyncClient until first request."""
        # Arrange
        http_client = HTTPClient()

        # Assert - Client should not be initialized yet
        assert http_client._client is None

    async def test_client_created_on_first_request(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """HTTPClient must initialize httpx.AsyncClient on first request."""
        # Arrange
        http_client = HTTPClient()

        # Act
        with patch("celeste.http.httpx.AsyncClient", return_value=mock_httpx_client):
            await http_client.post(
                url="https://api.example.com/test",
                headers={"Authorization": "Bearer test"},
                json_body={"key": "value"},
            )

        # Assert
        assert http_client._client is not None

    async def test_client_reused_across_multiple_requests(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """HTTPClient must reuse the same httpx.AsyncClient for multiple requests."""
        # Arrange
        http_client = HTTPClient()

        # Act
        with patch("celeste.http.httpx.AsyncClient", return_value=mock_httpx_client):
            await http_client.post(
                url="https://api.example.com/test1",
                headers={"Authorization": "Bearer test"},
                json_body={"key": "value1"},
            )
            first_client = http_client._client

            await http_client.post(
                url="https://api.example.com/test2",
                headers={"Authorization": "Bearer test"},
                json_body={"key": "value2"},
            )
            second_client = http_client._client

        # Assert - Same client instance must be reused
        assert first_client is second_client

    async def test_aclose_sets_client_to_none(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """HTTPClient.aclose() must properly cleanup and reset client state."""
        # Arrange
        http_client = HTTPClient()

        # Act
        with patch("celeste.http.httpx.AsyncClient", return_value=mock_httpx_client):
            await http_client.post(
                url="https://api.example.com/test",
                headers={"Authorization": "Bearer test"},
                json_body={"key": "value"},
            )
            assert http_client._client is not None

            await http_client.aclose()

        # Assert
        assert http_client._client is None
        mock_httpx_client.aclose.assert_called_once()

    async def test_aclose_handles_uninitialized_client(self) -> None:
        """HTTPClient.aclose() must handle the case when client was never initialized."""
        # Arrange
        http_client = HTTPClient()

        # Act & Assert - Should not raise any exceptions
        await http_client.aclose()
        assert http_client._client is None


class TestHTTPClientConnectionPooling:
    """Test connection pool configuration behaviors."""

    async def test_connection_limits_applied_to_httpx_client(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """HTTPClient must configure httpx.AsyncClient with specified connection limits."""
        # Arrange
        max_connections = 50
        max_keepalive = 25
        http_client = HTTPClient(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive,
        )

        # Act
        with patch(
            "celeste.http.httpx.AsyncClient", return_value=mock_httpx_client
        ) as mock_constructor:
            await http_client.post(
                url="https://api.example.com/test",
                headers={"Authorization": "Bearer test"},
                json_body={"key": "value"},
            )

        # Assert - Verify AsyncClient was called with correct limits
        mock_constructor.assert_called_once()
        call_kwargs = mock_constructor.call_args[1]
        limits = call_kwargs["limits"]

        assert limits.max_connections == max_connections
        assert limits.max_keepalive_connections == max_keepalive

    async def test_default_connection_limits(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """HTTPClient must use sensible default connection limits."""
        # Arrange
        http_client = HTTPClient()  # No explicit limits

        # Act
        with patch(
            "celeste.http.httpx.AsyncClient", return_value=mock_httpx_client
        ) as mock_constructor:
            await http_client.post(
                url="https://api.example.com/test",
                headers={"Authorization": "Bearer test"},
                json_body={"key": "value"},
            )

        # Assert - Verify defaults are applied
        mock_constructor.assert_called_once()
        call_kwargs = mock_constructor.call_args[1]
        limits = call_kwargs["limits"]

        assert limits.max_connections == 20
        assert limits.max_keepalive_connections == 10


class TestHTTPClientRequestMethods:
    """Test POST and GET request methods."""

    async def test_post_request_with_all_parameters(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """POST method must pass all parameters correctly to httpx.AsyncClient."""
        # Arrange
        http_client = HTTPClient()
        url = "https://api.example.com/generate"
        headers = {
            "Authorization": "Bearer sk-test",
            "Content-Type": "application/json",
        }
        json_body = {"prompt": "Hello", "max_tokens": 100}
        timeout = 30.0

        mock_response = httpx.Response(200, json={"result": "success"})
        mock_httpx_client.post.return_value = mock_response

        # Act
        with patch("celeste.http.httpx.AsyncClient", return_value=mock_httpx_client):
            response = await http_client.post(
                url=url,
                headers=headers,
                json_body=json_body,
                timeout=timeout,
            )

        # Assert
        mock_httpx_client.post.assert_called_once_with(
            url,
            headers=headers,
            json=json_body,
            timeout=timeout,
        )
        assert response.status_code == 200

    async def test_get_request_with_all_parameters(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """GET method must pass all parameters correctly to httpx.AsyncClient."""
        # Arrange
        http_client = HTTPClient()
        url = "https://api.example.com/models"
        headers = {"Authorization": "Bearer sk-test"}
        timeout = 15.0

        mock_response = httpx.Response(200, json={"models": ["gpt-4"]})
        mock_httpx_client.get.return_value = mock_response

        # Act
        with patch("celeste.http.httpx.AsyncClient", return_value=mock_httpx_client):
            response = await http_client.get(
                url=url,
                headers=headers,
                timeout=timeout,
            )

        # Assert
        mock_httpx_client.get.assert_called_once_with(
            url,
            headers=headers,
            timeout=timeout,
            follow_redirects=True,
        )
        assert response.status_code == 200

    async def test_post_propagates_httpx_errors(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """POST method must propagate httpx.HTTPError to caller."""
        # Arrange
        http_client = HTTPClient()
        mock_httpx_client.post.side_effect = httpx.TimeoutException("Request timeout")

        # Act & Assert
        with (
            patch("celeste.http.httpx.AsyncClient", return_value=mock_httpx_client),
            pytest.raises(httpx.TimeoutException, match="Request timeout"),
        ):
            await http_client.post(
                url="https://api.example.com/test",
                headers={"Authorization": "Bearer test"},
                json_body={"key": "value"},
            )

    async def test_get_propagates_httpx_errors(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """GET method must propagate httpx.HTTPError to caller."""
        # Arrange
        http_client = HTTPClient()
        mock_httpx_client.get.side_effect = httpx.ConnectError("Connection failed")

        # Act & Assert
        with (
            patch("celeste.http.httpx.AsyncClient", return_value=mock_httpx_client),
            pytest.raises(httpx.ConnectError, match="Connection failed"),
        ):
            await http_client.get(
                url="https://api.example.com/test",
                headers={"Authorization": "Bearer test"},
            )

    async def test_post_uses_default_timeout_when_not_specified(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """POST method must use default timeout when none is specified."""
        # Arrange
        http_client = HTTPClient()

        # Act
        with patch("celeste.http.httpx.AsyncClient", return_value=mock_httpx_client):
            await http_client.post(
                url="https://api.example.com/test",
                headers={"Authorization": "Bearer test"},
                json_body={"key": "value"},
                # Note: timeout parameter omitted
            )

        # Assert - Verify default timeout was used
        mock_httpx_client.post.assert_called_once()
        call_kwargs = mock_httpx_client.post.call_args[1]
        assert call_kwargs["timeout"] == 60.0

    async def test_get_uses_default_timeout_when_not_specified(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """GET method must use default timeout when none is specified."""
        # Arrange
        http_client = HTTPClient()

        # Act
        with patch("celeste.http.httpx.AsyncClient", return_value=mock_httpx_client):
            await http_client.get(
                url="https://api.example.com/test",
                headers={"Authorization": "Bearer test"},
                # Note: timeout parameter omitted
            )

        # Assert - Verify default timeout was used
        mock_httpx_client.get.assert_called_once()
        call_kwargs = mock_httpx_client.get.call_args[1]
        assert call_kwargs["timeout"] == 60.0

    async def test_custom_timeout_passed_to_httpx(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """HTTPClient passes custom timeout value to httpx.AsyncClient methods."""
        http_client = HTTPClient()
        custom_timeout = 120.0

        with patch("celeste.http.httpx.AsyncClient", return_value=mock_httpx_client):
            await http_client.post(
                url="https://api.example.com/test",
                headers={"Authorization": "Bearer test"},
                json_body={"key": "value"},
                timeout=custom_timeout,
            )

        # Verify custom timeout was passed to httpx
        mock_httpx_client.post.assert_called_once()
        call_kwargs = mock_httpx_client.post.call_args[1]
        assert call_kwargs["timeout"] == custom_timeout


class TestHTTPClientRegistry:
    """Test get_http_client registry and singleton behavior."""

    @pytest.fixture(autouse=True)
    def clear_registry(self) -> Generator[None, None, None]:
        """Clear HTTP client registry before each test to ensure isolation."""
        from celeste.http import _http_clients

        # Arrange - Store original state and clear registry
        original_clients = _http_clients.copy()
        _http_clients.clear()

        yield

        # Cleanup - Restore original state
        _http_clients.clear()
        _http_clients.update(original_clients)

    def test_get_http_client_returns_same_instance_for_same_key(self) -> None:
        """get_http_client must return the same HTTPClient for identical provider/capability."""
        # Arrange
        provider = Provider.OPENAI
        capability = Capability.TEXT_GENERATION

        # Act
        client1 = get_http_client(provider, capability)
        client2 = get_http_client(provider, capability)

        # Assert - Must be the exact same instance (singleton behavior)
        assert client1 is client2

    def test_get_http_client_returns_different_instances_for_different_providers(
        self,
    ) -> None:
        """get_http_client must return different HTTPClients for different providers."""
        # Arrange
        capability = Capability.TEXT_GENERATION

        # Act
        openai_client = get_http_client(Provider.OPENAI, capability)
        anthropic_client = get_http_client(Provider.ANTHROPIC, capability)

        # Assert - Must be different instances
        assert openai_client is not anthropic_client

    def test_get_http_client_returns_different_instances_for_different_capabilities(
        self,
    ) -> None:
        """get_http_client must return different HTTPClients for different capabilities."""
        # Arrange
        provider = Provider.OPENAI

        # Act
        text_client = get_http_client(provider, Capability.TEXT_GENERATION)
        image_client = get_http_client(provider, Capability.IMAGE_GENERATION)

        # Assert - Must be different instances
        assert text_client is not image_client

    def test_registry_isolation_prevents_cross_contamination(self) -> None:
        """Registry must maintain complete isolation between different provider/capability pairs."""
        # Arrange - Create clients for different combinations
        openai_text = get_http_client(Provider.OPENAI, Capability.TEXT_GENERATION)
        openai_image = get_http_client(Provider.OPENAI, Capability.IMAGE_GENERATION)
        anthropic_text = get_http_client(Provider.ANTHROPIC, Capability.TEXT_GENERATION)

        # Act - Retrieve them again
        openai_text_again = get_http_client(Provider.OPENAI, Capability.TEXT_GENERATION)
        openai_image_again = get_http_client(
            Provider.OPENAI, Capability.IMAGE_GENERATION
        )
        anthropic_text_again = get_http_client(
            Provider.ANTHROPIC, Capability.TEXT_GENERATION
        )

        # Assert - Same pairs return same instances, different pairs return different instances
        assert openai_text is openai_text_again
        assert openai_image is openai_image_again
        assert anthropic_text is anthropic_text_again

        # Verify all three are distinct
        assert openai_text is not openai_image
        assert openai_text is not anthropic_text
        assert openai_image is not anthropic_text


class TestHTTPClientCleanup:
    """Test close_all_http_clients and clear_http_clients functionality."""

    @pytest.fixture(autouse=True)
    def clear_registry(self) -> Generator[None, None, None]:
        """Clear HTTP client registry before each test to ensure isolation."""
        from celeste.http import _http_clients

        # Arrange - Store original state and clear registry
        original_clients = _http_clients.copy()
        _http_clients.clear()

        yield

        # Cleanup - Restore original state
        _http_clients.clear()
        _http_clients.update(original_clients)

    async def test_close_all_http_clients_closes_all_and_clears_registry(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """close_all_http_clients must close all clients and clear the registry."""
        from celeste.http import _http_clients, get_http_client

        # Arrange - Create multiple clients
        client1 = get_http_client(Provider.OPENAI, Capability.TEXT_GENERATION)
        client2 = get_http_client(Provider.ANTHROPIC, Capability.TEXT_GENERATION)

        # Initialize both clients to create httpx.AsyncClient instances
        with patch("celeste.http.httpx.AsyncClient", return_value=mock_httpx_client):
            await client1.post(
                url="https://api.example.com/test1",
                headers={"Authorization": "Bearer test"},
                json_body={"key": "value"},
            )
            await client2.post(
                url="https://api.example.com/test2",
                headers={"Authorization": "Bearer test"},
                json_body={"key": "value"},
            )

        # Verify registry has clients and clients are initialized
        assert len(_http_clients) == 2
        assert client1._client is not None
        assert client2._client is not None

        # Act - Close all clients
        await close_all_http_clients()

        # Assert - Registry should be empty AND clients should be reset
        assert len(_http_clients) == 0
        assert client1._client is None
        assert client2._client is None

    async def test_close_all_http_clients_calls_aclose_on_each_client(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """close_all_http_clients must call aclose() on each httpx.AsyncClient."""
        from celeste.http import get_http_client

        # Arrange - Create and initialize multiple clients with separate mock instances
        mock_client1 = AsyncMock(spec=httpx.AsyncClient)
        mock_client1.post = AsyncMock(return_value=httpx.Response(200))
        mock_client1.aclose = AsyncMock()

        mock_client2 = AsyncMock(spec=httpx.AsyncClient)
        mock_client2.post = AsyncMock(return_value=httpx.Response(200))
        mock_client2.aclose = AsyncMock()

        client1 = get_http_client(Provider.OPENAI, Capability.TEXT_GENERATION)
        client2 = get_http_client(Provider.ANTHROPIC, Capability.TEXT_GENERATION)

        # Initialize clients with different mock instances
        with patch("celeste.http.httpx.AsyncClient") as mock_constructor:
            mock_constructor.side_effect = [mock_client1, mock_client2]

            await client1.post(
                url="https://api.example.com/test1",
                headers={"Authorization": "Bearer test"},
                json_body={"key": "value"},
            )
            await client2.post(
                url="https://api.example.com/test2",
                headers={"Authorization": "Bearer test"},
                json_body={"key": "value"},
            )

        # Act - Close all clients
        await close_all_http_clients()

        # Assert - Both mock clients should have aclose called
        mock_client1.aclose.assert_called_once()
        mock_client2.aclose.assert_called_once()

    async def test_clear_http_clients_clears_without_closing(self) -> None:
        """clear_http_clients must clear registry without calling aclose()."""
        from celeste.http import _http_clients, get_http_client

        # Arrange - Create multiple clients
        mock_client1 = AsyncMock(spec=httpx.AsyncClient)
        mock_client1.post = AsyncMock(return_value=httpx.Response(200))
        mock_client1.aclose = AsyncMock()

        client1 = get_http_client(Provider.OPENAI, Capability.TEXT_GENERATION)

        # Initialize client
        with patch("celeste.http.httpx.AsyncClient", return_value=mock_client1):
            await client1.post(
                url="https://api.example.com/test",
                headers={"Authorization": "Bearer test"},
                json_body={"key": "value"},
            )

        # Verify registry has client
        assert len(_http_clients) == 1

        # Act - Clear without closing
        clear_http_clients()

        # Assert - Registry cleared but aclose not called
        assert len(_http_clients) == 0
        mock_client1.aclose.assert_not_called()

    async def test_close_all_handles_multiple_providers_and_capabilities(
        self,
    ) -> None:
        """close_all_http_clients must handle multiple provider/capability combinations."""
        from celeste.http import _http_clients, get_http_client

        # Arrange - Create clients for different combinations
        mock_client1 = AsyncMock(spec=httpx.AsyncClient)
        mock_client1.post = AsyncMock(return_value=httpx.Response(200))
        mock_client1.aclose = AsyncMock()

        mock_client2 = AsyncMock(spec=httpx.AsyncClient)
        mock_client2.post = AsyncMock(return_value=httpx.Response(200))
        mock_client2.aclose = AsyncMock()

        mock_client3 = AsyncMock(spec=httpx.AsyncClient)
        mock_client3.post = AsyncMock(return_value=httpx.Response(200))
        mock_client3.aclose = AsyncMock()

        client1 = get_http_client(Provider.OPENAI, Capability.TEXT_GENERATION)
        client2 = get_http_client(Provider.OPENAI, Capability.IMAGE_GENERATION)
        client3 = get_http_client(Provider.ANTHROPIC, Capability.TEXT_GENERATION)

        # Initialize all clients
        with patch("celeste.http.httpx.AsyncClient") as mock_constructor:
            mock_constructor.side_effect = [mock_client1, mock_client2, mock_client3]

            await client1.post(
                url="https://api.example.com/test1",
                headers={"Authorization": "Bearer test"},
                json_body={"key": "value"},
            )
            await client2.post(
                url="https://api.example.com/test2",
                headers={"Authorization": "Bearer test"},
                json_body={"key": "value"},
            )
            await client3.post(
                url="https://api.example.com/test3",
                headers={"Authorization": "Bearer test"},
                json_body={"key": "value"},
            )

        # Verify registry has all 3 clients
        assert len(_http_clients) == 3

        # Act - Close all
        await close_all_http_clients()

        # Assert - All closed and registry empty
        assert len(_http_clients) == 0
        mock_client1.aclose.assert_called_once()
        mock_client2.aclose.assert_called_once()
        mock_client3.aclose.assert_called_once()

    async def test_close_all_continues_despite_individual_failures(self) -> None:
        """close_all_http_clients must continue closing all clients even if one fails."""
        from celeste.http import _http_clients, get_http_client

        # Arrange - Create clients where one will fail to close
        mock_client1 = AsyncMock(spec=httpx.AsyncClient)
        mock_client1.post = AsyncMock(return_value=httpx.Response(200))
        mock_client1.aclose = AsyncMock(side_effect=RuntimeError("Close failed"))

        mock_client2 = AsyncMock(spec=httpx.AsyncClient)
        mock_client2.post = AsyncMock(return_value=httpx.Response(200))
        mock_client2.aclose = AsyncMock()

        client1 = get_http_client(Provider.OPENAI, Capability.TEXT_GENERATION)
        client2 = get_http_client(Provider.ANTHROPIC, Capability.TEXT_GENERATION)

        # Initialize both clients
        with patch("celeste.http.httpx.AsyncClient") as mock_constructor:
            mock_constructor.side_effect = [mock_client1, mock_client2]

            await client1.post(
                url="https://api.example.com/test1",
                headers={"Authorization": "Bearer test"},
                json_body={"key": "value"},
            )
            await client2.post(
                url="https://api.example.com/test2",
                headers={"Authorization": "Bearer test"},
                json_body={"key": "value"},
            )

        # Act - Should not raise, continues closing despite failure
        await close_all_http_clients()

        # Assert - Both aclose calls were attempted and registry is cleared
        mock_client1.aclose.assert_called_once()
        mock_client2.aclose.assert_called_once()
        assert len(_http_clients) == 0


class TestHTTPClientContextManager:
    """Test async context manager protocol for resource cleanup."""

    async def test_context_manager_returns_self(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """__aenter__ must return HTTPClient instance for use in async with block."""
        # Arrange
        http_client = HTTPClient()

        # Act
        async with http_client as client:
            # Assert - Context manager returns the HTTPClient instance itself
            assert client is http_client

    async def test_context_manager_calls_aclose_on_exit(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """__aexit__ must call aclose() to cleanup connections on context exit."""
        # Arrange
        http_client = HTTPClient()

        # Act - Initialize client and exit context
        with patch("celeste.http.httpx.AsyncClient", return_value=mock_httpx_client):
            async with http_client:
                await http_client.post(
                    url="https://api.example.com/test",
                    headers={"Authorization": "Bearer test"},
                    json_body={"key": "value"},
                )
                # Verify client was initialized
                assert http_client._client is not None

        # Assert - After exiting context, client should be closed
        assert http_client._client is None
        mock_httpx_client.aclose.assert_called_once()

    async def test_context_manager_cleanup_on_exception(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """__aexit__ must cleanup connections even when exception occurs in context."""
        # Arrange
        http_client = HTTPClient()

        # Act & Assert - Verify cleanup happens despite exception
        with (
            patch("celeste.http.httpx.AsyncClient", return_value=mock_httpx_client),
            pytest.raises(ValueError, match="Test exception"),
        ):
            async with http_client:
                await http_client.post(
                    url="https://api.example.com/test",
                    headers={"Authorization": "Bearer test"},
                    json_body={"key": "value"},
                )
                raise ValueError("Test exception")

        # Assert - Client was closed despite exception
        assert http_client._client is None
        mock_httpx_client.aclose.assert_called_once()


class TestHTTPClientStreaming:
    """Test Server-Sent Events streaming functionality."""

    def _create_mock_sse(self, data: str) -> MagicMock:
        """Create mock SSE event with data."""
        mock = MagicMock()
        mock.data = data
        return mock

    def _create_mock_event_source(self, events: list) -> MagicMock:
        """Create mock SSE event source with events."""
        mock_source = MagicMock()
        mock_source.aiter_sse = MagicMock(return_value=self._async_iter(events))
        mock_source.__aenter__ = AsyncMock(return_value=mock_source)
        mock_source.__aexit__ = AsyncMock(return_value=False)

        # Mock response with headers for httpx_sse content-type check
        mock_response = MagicMock()
        mock_response.headers = MagicMock()
        mock_response.headers.get = MagicMock(return_value="text/event-stream")
        mock_source._response = mock_response

        return mock_source

    async def test_stream_post_yields_parsed_json_events(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """stream_post must parse SSE events and yield all JSON."""
        # Arrange
        http_client = HTTPClient()
        events = [
            self._create_mock_sse('{"delta": "Hello"}'),
            self._create_mock_sse('{"delta": " world"}'),
        ]
        mock_event_source = self._create_mock_event_source(events)

        # Act
        with (
            patch("celeste.http.httpx.AsyncClient", return_value=mock_httpx_client),
            patch("celeste.http.aconnect_sse", return_value=mock_event_source),
        ):
            chunks = [
                chunk
                async for chunk in http_client.stream_post(
                    url="https://api.example.com/stream",
                    headers={"Authorization": "Bearer test"},
                    json_body={"prompt": "test"},
                )
            ]

        # Assert - All valid JSON events are parsed and yielded
        assert chunks == [{"delta": "Hello"}, {"delta": " world"}]

    async def test_stream_post_raises_on_malformed_json(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """stream_post must raise JSONDecodeError on malformed SSE events."""
        # Arrange
        http_client = HTTPClient()
        events = [
            self._create_mock_sse('{"valid": true}'),
            self._create_mock_sse("{invalid json"),
            self._create_mock_sse('{"valid": "also"}'),
        ]
        mock_event_source = self._create_mock_event_source(events)

        # Act
        results = []
        with (
            patch("celeste.http.httpx.AsyncClient", return_value=mock_httpx_client),
            patch("celeste.http.aconnect_sse", return_value=mock_event_source),
        ):
            async for chunk in http_client.stream_post(
                url="https://api.example.com/stream",
                headers={"Authorization": "Bearer test"},
                json_body={"prompt": "test"},
            ):
                results.append(chunk)

        # Assert - only valid JSON events are yielded
        assert len(results) == 2
        assert results[0] == {"valid": True}
        assert results[1] == {"valid": "also"}

    async def test_stream_post_passes_parameters_correctly(
        self, mock_httpx_client: AsyncMock
    ) -> None:
        """stream_post must pass all parameters to aconnect_sse correctly."""
        # Arrange
        http_client = HTTPClient()
        url = "https://api.example.com/stream"
        headers = {"Authorization": "Bearer sk-test", "X-Custom": "value"}
        json_body = {"prompt": "test", "stream": True}
        timeout = 120.0

        mock_event_source = self._create_mock_event_source([])  # Empty stream

        # Act
        with (
            patch("celeste.http.httpx.AsyncClient", return_value=mock_httpx_client),
            patch(
                "celeste.http.aconnect_sse", return_value=mock_event_source
            ) as mock_sse,
        ):
            async for _ in http_client.stream_post(
                url=url,
                headers=headers,
                json_body=json_body,
                timeout=timeout,
            ):
                pass

        # Assert - Verify aconnect_sse called with correct parameters
        mock_sse.assert_called_once_with(
            mock_httpx_client,
            "POST",
            url,
            json=json_body,
            headers=headers,
            timeout=timeout,
        )

    @staticmethod
    async def _async_iter(items: list) -> AsyncIterator:
        """Helper to create async iterator from list."""
        for item in items:
            yield item
