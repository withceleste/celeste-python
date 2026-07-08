"""Tool kind discriminator: JSON round-trips rehydrate; garbage dicts fail hard."""

import pytest

from celeste.exceptions import InvalidToolError
from celeste.modalities.text.io import TextInput
from celeste.tools import WebSearch
from tests.unit_tests.conftest import anthropic_test_client


def test_build_request_rehydrates_serialized_tools() -> None:
    dumped = WebSearch(max_uses=3).model_dump(mode="json")

    request = anthropic_test_client()._build_request(
        TextInput(prompt="hi"), tools=[dumped]
    )

    assert request["tools"] == [
        {"type": "web_search_20260209", "name": "web_search", "max_uses": 3}
    ]


def test_tools_mapper_rejects_unrecognized_dict() -> None:
    with pytest.raises(InvalidToolError):
        anthropic_test_client()._build_request(
            TextInput(prompt="hi"), tools=[{"allowed_domains": None}]
        )
