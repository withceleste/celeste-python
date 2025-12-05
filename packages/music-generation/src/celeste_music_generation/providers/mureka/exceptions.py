"""Mureka-specific exceptions."""


class MurekaError(Exception):
    """Base exception for Mureka API errors."""

    def __init__(self, message: str, status_code: int | None = None, trace_id: str | None = None) -> None:
        self.message = message
        self.status_code = status_code
        self.trace_id = trace_id
        super().__init__(self.message)


class MurekaInvalidRequestError(MurekaError):
    """400 - Invalid Request.

    The request parameters are incorrect.
    Refer to the documentation to input the correct request parameters.
    """


class MurekaAuthenticationError(MurekaError):
    """401 - Invalid Authentication.

    Invalid Authentication. Ensure the correct API key is being used.
    """


class MurekaForbiddenError(MurekaError):
    """403 - Forbidden.

    You are accessing the API from an unsupported region.
    Ensure your access is from a supported region.
    """


class MurekaRateLimitError(MurekaError):
    """429 - Rate limit reached for requests.

    You are sending requests too quickly.
    Pace your requests. Check the concurrent request limit in the pricing plans.
    """


class MurekaQuotaExceededError(MurekaError):
    """429 - You exceeded your current quota.

    You have run out of credits. Buy more credits.
    """


class MurekaServerError(MurekaError):
    """500 - The server had an error while processing your request.

    Issue on our servers.
    Retry your request after a brief wait and contact us if the issue persists.
    """


class MurekaOverloadedError(MurekaError):
    """503 - The engine is currently overloaded.

    Our servers are experiencing high traffic.
    Please retry your requests after a brief wait.
    """


def raise_mureka_error(status_code: int, message: str, trace_id: str | None = None) -> None:
    """Raise appropriate Mureka exception based on status code and message."""
    error_message = f"{message} (trace_id: {trace_id})" if trace_id else message

    if status_code == 400:
        raise MurekaInvalidRequestError(error_message, status_code, trace_id)
    elif status_code == 401:
        raise MurekaAuthenticationError(error_message, status_code, trace_id)
    elif status_code == 403:
        raise MurekaForbiddenError(error_message, status_code, trace_id)
    elif status_code == 429:
        # Differentiate between rate limit and quota exceeded
        if "quota" in message.lower() or "credits" in message.lower():
            raise MurekaQuotaExceededError(error_message, status_code, trace_id)
        else:
            raise MurekaRateLimitError(error_message, status_code, trace_id)
    elif status_code == 500:
        raise MurekaServerError(error_message, status_code, trace_id)
    elif status_code == 503:
        raise MurekaOverloadedError(error_message, status_code, trace_id)
    else:
        raise MurekaError(error_message, status_code, trace_id)


__all__ = [
    "MurekaAuthenticationError",
    "MurekaError",
    "MurekaForbiddenError",
    "MurekaInvalidRequestError",
    "MurekaOverloadedError",
    "MurekaQuotaExceededError",
    "MurekaRateLimitError",
    "MurekaServerError",
    "raise_mureka_error",
]
