"""Pytest configuration and fixtures for integration tests."""

from collections.abc import AsyncGenerator
from typing import Any

import pytest_asyncio

from celeste.http import close_all_http_clients


@pytest_asyncio.fixture(autouse=True)
async def cleanup_http_clients() -> AsyncGenerator[None, None]:
    """Ensure HTTP clients are closed after each test.

    This fixture runs automatically after each test to ensure HTTP clients
    are properly closed before pytest-asyncio closes the event loop.
    This prevents "Event loop is closed" errors when using pytest-xdist.
    """
    yield
    await close_all_http_clients()


def pytest_configure(config: Any) -> None:  # noqa: ANN401
    config.addinivalue_line("markers", "integration: mark test as an integration test")
