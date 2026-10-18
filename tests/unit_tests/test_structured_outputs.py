"""Structured-output schema transformations."""

import json
from collections.abc import Iterator

import pytest
from pydantic import BaseModel, TypeAdapter

from celeste.constraints import Schema
from celeste.modalities.text.protocols.openresponses.parameters import (
    OutputSchemaMapper as OpenResponsesOutputSchemaMapper,
)
from celeste.modalities.text.providers.anthropic.parameters import (
    OutputSchemaMapper as AnthropicOutputSchemaMapper,
)
from celeste.modalities.text.providers.huggingface.parameters import (
    OutputSchemaMapper as HuggingFaceOutputSchemaMapper,
)
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.structured_outputs import (
    RefResolvingJsonSchemaGenerator,
    StrictJsonSchemaGenerator,
    StrictRefResolvingJsonSchemaGenerator,
)


class Leaf(BaseModel):
    value: int
    label: str = "default"


class Container(BaseModel):
    leaf: Leaf
    items: list[Leaf]


def _schema(generator: type) -> dict:
    return TypeAdapter(Container).json_schema(schema_generator=generator)


def test_strict_schema_closes_every_object_and_requires_defaults() -> None:
    schema = _schema(StrictJsonSchemaGenerator)

    assert schema["additionalProperties"] is False
    leaf = schema["$defs"]["Leaf"]
    assert leaf["additionalProperties"] is False
    assert set(leaf["required"]) == {"value", "label"}


def test_strict_schema_preserves_explicit_additional_properties() -> None:
    schema = {"type": "object", "additionalProperties": True}
    StrictJsonSchemaGenerator(ref_template="{model}")._add_strict_props(schema)
    assert schema["additionalProperties"] is True


def test_ref_resolver_inlines_nested_and_list_references() -> None:
    schema = _schema(RefResolvingJsonSchemaGenerator)

    assert "$defs" not in schema
    assert "$ref" not in str(schema)
    assert schema["properties"]["leaf"]["properties"]["value"]["type"] == "integer"
    assert schema["properties"]["items"]["items"]["type"] == "object"


def test_combined_generator_applies_both_contracts() -> None:
    schema = _schema(StrictRefResolvingJsonSchemaGenerator)

    assert "$defs" not in schema
    assert "$ref" not in str(schema)
    assert schema["additionalProperties"] is False
    assert schema["properties"]["leaf"]["additionalProperties"] is False
    assert schema["properties"]["items"]["items"]["additionalProperties"] is False


class Tree(BaseModel):
    value: int
    children: list["Tree"]


def _schema_nodes(value: object) -> Iterator[dict]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _schema_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from _schema_nodes(child)


@pytest.mark.parametrize(
    ("mapper", "path", "wrapped"),
    [
        (OpenResponsesOutputSchemaMapper(), ("text", "format"), True),
        (AnthropicOutputSchemaMapper(), ("output_config", "format"), False),
        (HuggingFaceOutputSchemaMapper(), ("response_format", "json_schema"), True),
    ],
    ids=["openresponses", "anthropic", "huggingface"],
)
@pytest.mark.parametrize(
    ("output_schema", "expected"),
    [
        (list[Leaf], [Leaf(value=1)]),
        (list[Container], [Container(leaf=Leaf(value=1), items=[Leaf(value=2)])]),
        (list[Tree], [Tree(value=1, children=[Tree(value=2, children=[])])]),
        (Container, Container(leaf=Leaf(value=1), items=[Leaf(value=2)])),
    ],
    ids=["plain-list", "nested-list", "recursive-list", "single-model"],
)
def test_output_schema_references_and_typed_round_trip(
    mapper: ParameterMapper,
    path: tuple[str, ...],
    wrapped: bool,
    output_schema: object,
    expected: BaseModel | list[BaseModel],
) -> None:
    model = Model(
        id="schema-test",
        display_name="Schema test",
        parameter_constraints={mapper.name: Schema()},
    )
    wire = mapper.map({}, output_schema, model)
    for key in path:
        wire = wire[key]
    schema = wire["schema"]
    is_list = isinstance(expected, list)
    if is_list and wrapped:
        assert schema["type"] == "object"
        assert schema["properties"]["items"]["type"] == "array"
        assert schema["required"] == ["items"]
        if path[0] == "text":
            assert schema["additionalProperties"] is False
    else:
        assert schema["type"] == ("array" if is_list else "object")
    if path[0] != "output_config":
        assert wire["strict"] is True

    for node in _schema_nodes(schema):
        if (ref := node.get("$ref")) and ref.startswith("#/"):
            target = schema
            for token in ref[2:].split("/"):
                target = target[token.replace("~1", "/").replace("~0", "~")]
            assert isinstance(target, (dict, bool))
        # Check generated model objects, separately from provider list wrappers.
        if node.get("type") == "object" and (not is_list or node is not schema):
            assert node["additionalProperties"] is False
            assert set(node["required"]) == set(node["properties"])

    payload = TypeAdapter(output_schema).dump_python(expected, mode="json")
    if is_list and wrapped:
        payload = {"items": payload}
    parsed = mapper.parse_output(json.dumps(payload), output_schema)
    assert parsed == expected
    assert type(parsed) is type(expected)
