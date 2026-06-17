"""Tests for the no-op telemetry proxy used when opentelemetry-api is absent."""

from celeste.telemetry import _NoOp, _noop_use_span


def test_noop_proxy_supports_all_call_shapes() -> None:
    """The _NoOp proxy must satisfy every span/meter/Status call site used in telemetry."""
    noop = _NoOp()

    # tracer.start_as_current_span(...) used as a context manager yielding a span
    with noop.start_as_current_span("op") as span:
        span.set_attribute("k", "v")
        span.set_attributes({"k": "v"})
        span.add_event("e", {"a": 1})
        span.record_exception(Exception("boom"))
        span.set_status(_NoOp(_NoOp.ERROR, "msg"))  # Status(StatusCode.ERROR, msg)
        span.end()

    # StatusCode.ERROR is read as a real class attribute
    assert _NoOp.ERROR == "ERROR"

    # meter.create_histogram(...).record(...) chains through the proxy
    histogram = noop.create_histogram(name="n", unit="{token}", description="d")
    histogram.record(1.0, {"gen_ai.token.type": "input"})


def test_noop_use_span_yields_the_passed_span() -> None:
    """_noop_use_span must yield the span it was given, not a no-op stand-in."""
    sentinel = object()
    with _noop_use_span(sentinel) as span:
        assert span is sentinel
