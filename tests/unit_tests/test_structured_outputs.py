"""Structured-output schema transformations."""

from pydantic import BaseModel, TypeAdapter

from celeste.structured_outputs import StrictJsonSchemaGenerator


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
