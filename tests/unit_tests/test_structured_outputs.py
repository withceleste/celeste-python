"""Structured-output schema transformations."""

from pydantic import BaseModel, TypeAdapter

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
