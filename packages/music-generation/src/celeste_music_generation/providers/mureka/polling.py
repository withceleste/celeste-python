"""Async task polling for Mureka API."""

import asyncio
import logging
from typing import Any

from celeste.exceptions import Error
from celeste.http import HTTPClient

from . import config

logger = logging.getLogger(__name__)


class TaskPollingError(Error):
    """Error during task polling."""

    pass


class TaskTimeoutError(TaskPollingError):
    """Task polling timed out."""

    pass


class TaskFailedError(TaskPollingError):
    """Task failed on provider side."""

    pass


async def poll_task(
    http_client: HTTPClient,
    task_id: str,
    query_endpoint: str,
    auth_header: str,
    poll_interval: float = config.DEFAULT_POLL_INTERVAL,
    max_attempts: int = config.MAX_POLL_ATTEMPTS,
) -> dict[str, Any]:
    """Poll a Mureka task until completion or failure.

    Args:
        http_client: HTTP client instance
        task_id: Task ID to poll
        query_endpoint: Query endpoint URL (e.g., /v1/song/query)
        auth_header: Full authorization header value
        poll_interval: Seconds between polls
        max_attempts: Maximum polling attempts before timeout

    Returns:
        Final task response data when succeeded

    Raises:
        TaskTimeoutError: If max attempts reached
        TaskFailedError: If task failed on provider side
        TaskPollingError: For other polling errors
    """
    headers = {
        config.AUTH_HEADER_NAME: auth_header,
        "Content-Type": "application/json",
    }

    query_url = f"{config.BASE_URL}{query_endpoint}/{task_id}"

    for attempt in range(max_attempts):
        try:
            response = await http_client.get(query_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            status = data.get("status")
            trace_id = data.get("trace_id")

            # Log trace_id for debugging
            if trace_id:
                logger.debug(f"Task {task_id} trace_id: {trace_id}")

            # Check terminal statuses
            if status == config.TASK_STATUS_SUCCEEDED:
                logger.info(f"Task {task_id} succeeded after {attempt + 1} attempts")
                return data

            if status == config.TASK_STATUS_FAILED:
                error_message = data.get("error", "Task failed without error message")
                msg = f"Task {task_id} failed: {error_message}"
                raise TaskFailedError(msg)

            # Continue polling for non-terminal statuses
            logger.debug(
                f"Task {task_id} status: {status} (attempt {attempt + 1}/{max_attempts})"
            )
            await asyncio.sleep(poll_interval)

        except TaskFailedError:
            raise
        except Exception as e:
            msg = f"Error polling task {task_id}: {e}"
            logger.error(msg)
            raise TaskPollingError(msg) from e

    # Timeout
    msg = f"Task {task_id} polling timed out after {max_attempts} attempts"
    raise TaskTimeoutError(msg)


__all__ = [
    "TaskFailedError",
    "TaskPollingError",
    "TaskTimeoutError",
    "poll_task",
]
