"""Regression coverage for Google Interactions API step reconstruction."""

from __future__ import annotations

from celeste.providers.google.interactions.streaming import reconstruct_steps
from celeste.providers.google.interactions.tools import tool_calls_from_steps


def test_reconstructs_text_step_from_deltas() -> None:
    events = [
        {"index": 0, "step": {"type": "model_output"}, "event_type": "step.start"},
        {
            "index": 0,
            "delta": {"type": "text", "text": "1, 2, 3, "},
            "event_type": "step.delta",
        },
        {
            "index": 0,
            "delta": {"type": "text", "text": "4, 5, 6"},
            "event_type": "step.delta",
        },
        {"index": 0, "event_type": "step.stop"},
    ]

    steps = reconstruct_steps(events)

    assert steps == [
        {
            "type": "model_output",
            "content": [{"type": "text", "text": "1, 2, 3, 4, 5, 6"}],
        }
    ]


def test_reconstructs_function_call_with_accumulated_arguments() -> None:
    events = [
        {
            "index": 0,
            "step": {
                "type": "function_call",
                "id": "un6k8t18",
                "name": "get_weather",
                "arguments": {},
            },
            "event_type": "step.start",
        },
        {
            "index": 0,
            "delta": {"type": "arguments_delta", "arguments": '{"location":'},
            "event_type": "step.delta",
        },
        {
            "index": 0,
            "delta": {"type": "arguments_delta", "arguments": '"San Francisco, CA"}'},
            "event_type": "step.delta",
        },
        {"index": 0, "event_type": "step.stop"},
    ]

    steps = reconstruct_steps(events)
    tool_calls = tool_calls_from_steps(steps)

    assert len(tool_calls) == 1
    assert tool_calls[0].name == "get_weather"
    assert tool_calls[0].arguments == {"location": "San Francisco, CA"}


def test_reconstructs_thought_step_with_summary_and_signature() -> None:
    events = [
        {"index": 0, "step": {"type": "thought"}, "event_type": "step.start"},
        {
            "index": 0,
            "delta": {
                "type": "thought_summary",
                "content": {"type": "text", "text": "Implementing... "},
            },
            "event_type": "step.delta",
        },
        {
            "index": 0,
            "delta": {
                "type": "thought_summary",
                "content": {"type": "text", "text": "done."},
            },
            "event_type": "step.delta",
        },
        {
            "index": 0,
            "delta": {"type": "thought_signature", "signature": "sig-abc"},
            "event_type": "step.delta",
        },
        {"index": 0, "event_type": "step.stop"},
    ]

    steps = reconstruct_steps(events)

    assert steps == [
        {
            "type": "thought",
            "summary": [{"type": "text", "text": "Implementing... done."}],
            "signature": "sig-abc",
        }
    ]


def test_reconstructs_interleaved_steps_by_index() -> None:
    thought_events = [
        {"index": 0, "step": {"type": "thought"}, "event_type": "step.start"},
        {
            "index": 0,
            "delta": {
                "type": "thought_summary",
                "content": {"type": "text", "text": "thinking..."},
            },
            "event_type": "step.delta",
        },
        {"index": 0, "event_type": "step.stop"},
    ]
    call_events = [
        {
            "index": 1,
            "step": {
                "type": "function_call",
                "id": "call-1",
                "name": "get_weather",
                "arguments": {},
            },
            "event_type": "step.start",
        },
        {
            "index": 1,
            "delta": {"type": "arguments_delta", "arguments": '{"location": "Paris"}'},
            "event_type": "step.delta",
        },
        {"index": 1, "event_type": "step.stop"},
    ]

    steps = reconstruct_steps(thought_events + call_events)

    assert [step["type"] for step in steps] == ["thought", "function_call"]
    assert steps[1]["arguments"] == {"location": "Paris"}


def test_reconstructs_text_annotations_and_search_steps() -> None:
    events = [
        {
            "index": 0,
            "step": {"type": "google_search_call", "id": "s1", "signature": "sig-"},
            "event_type": "step.start",
        },
        {
            "index": 0,
            "delta": {
                "type": "google_search_call",
                "arguments": {"queries": ["celeste sdk"]},
                "signature": "call",
            },
            "event_type": "step.delta",
        },
        {"index": 0, "event_type": "step.stop"},
        {
            "index": 1,
            "step": {"type": "google_search_result"},
            "event_type": "step.start",
        },
        {
            "index": 1,
            "delta": {
                "type": "google_search_result",
                "result": [{"search_suggestions": "<div/>"}],
            },
            "event_type": "step.delta",
        },
        {"index": 1, "event_type": "step.stop"},
        {"index": 2, "step": {"type": "model_output"}, "event_type": "step.start"},
        {
            "index": 2,
            "delta": {"type": "text", "text": "Celeste is a Python SDK."},
            "event_type": "step.delta",
        },
        {
            "index": 2,
            "delta": {
                "type": "text_annotation_delta",
                "annotations": [{"type": "url_citation", "url": "https://example.com"}],
            },
            "event_type": "step.delta",
        },
        {"index": 2, "event_type": "step.stop"},
    ]

    steps = reconstruct_steps(events)

    assert steps[0]["arguments"] == {"queries": ["celeste sdk"]}
    assert steps[0]["signature"] == "sig-call"
    assert steps[1]["result"] == [{"search_suggestions": "<div/>"}]
    annotations = steps[2]["content"][0]["annotations"]
    assert annotations[0]["type"] == "url_citation"
    assert annotations[0]["url"] == "https://example.com"


def test_step_without_stop_is_dropped() -> None:
    events = [
        {"index": 0, "step": {"type": "model_output"}, "event_type": "step.start"},
        {
            "index": 0,
            "delta": {"type": "text", "text": "incomplete"},
            "event_type": "step.delta",
        },
    ]

    assert reconstruct_steps(events) == []
