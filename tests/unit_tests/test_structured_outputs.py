"""Tests for JSON Schema generators for structured outputs."""

from pydantic import BaseModel, TypeAdapter

from celeste.structured_outputs import (
    RefResolvingJsonSchemaGenerator,
    StrictJsonSchemaGenerator,
    StrictRefResolvingJsonSchemaGenerator,
)


class TestStrictJsonSchemaGenerator:
    """Test StrictJsonSchemaGenerator adds additionalProperties: false."""

    def test_adds_additional_properties_false_to_simple_object(self) -> None:
        """Object schemas get additionalProperties: false."""

        class SimpleModel(BaseModel):
            name: str

        schema = TypeAdapter(SimpleModel).json_schema(
            schema_generator=StrictJsonSchemaGenerator
        )

        assert schema.get("additionalProperties") is False

    def test_preserves_existing_additional_properties(self) -> None:
        """Doesn't override existing additionalProperties when already set."""
        generator = StrictJsonSchemaGenerator(ref_template="{model}")
        schema: dict = {"type": "object", "additionalProperties": True}

        generator._add_strict_props(schema)

        assert schema["additionalProperties"] is True

    def test_recursively_applies_to_nested_objects(self) -> None:
        """Nested objects also get additionalProperties: false."""

        class InnerModel(BaseModel):
            value: int

        class OuterModel(BaseModel):
            inner: InnerModel

        schema = TypeAdapter(OuterModel).json_schema(
            schema_generator=StrictJsonSchemaGenerator
        )

        # Root should have additionalProperties: false
        assert schema.get("additionalProperties") is False

        # Nested object in $defs should also have it
        inner_def = schema.get("$defs", {}).get("InnerModel", {})
        assert inner_def.get("additionalProperties") is False

    def test_handles_array_items(self) -> None:
        """Objects in array items get additionalProperties: false."""

        class ItemModel(BaseModel):
            id: int

        class ContainerModel(BaseModel):
            items: list[ItemModel]

        schema = TypeAdapter(ContainerModel).json_schema(
            schema_generator=StrictJsonSchemaGenerator
        )

        assert schema.get("additionalProperties") is False
        # ItemModel in $defs should also have it
        item_def = schema.get("$defs", {}).get("ItemModel", {})
        assert item_def.get("additionalProperties") is False

    def test_ignores_non_object_types(self) -> None:
        """Non-object schemas don't get additionalProperties."""

        class StringModel(BaseModel):
            name: str

        schema = TypeAdapter(StringModel).json_schema(
            schema_generator=StrictJsonSchemaGenerator
        )

        # String field itself shouldn't have additionalProperties
        name_prop = schema.get("properties", {}).get("name", {})
        assert "additionalProperties" not in name_prop

    def test_handles_non_dict_input_gracefully(self) -> None:
        """_add_strict_props handles non-dict input without error."""
        generator = StrictJsonSchemaGenerator(ref_template="{model}")

        # Should not raise
        generator._add_strict_props(None)  # type: ignore[arg-type]
        generator._add_strict_props([1, 2, 3])  # type: ignore[arg-type]
        generator._add_strict_props("string")  # type: ignore[arg-type]


class TestRefResolvingJsonSchemaGenerator:
    """Test RefResolvingJsonSchemaGenerator resolves $ref inline."""

    def test_resolves_simple_ref(self) -> None:
        """$ref replaced with definition content."""

        class ReferencedModel(BaseModel):
            x: int

        class ContainerModel(BaseModel):
            ref: ReferencedModel

        schema = TypeAdapter(ContainerModel).json_schema(
            schema_generator=RefResolvingJsonSchemaGenerator
        )

        # After resolution, no $ref should remain in properties
        ref_prop = schema.get("properties", {}).get("ref", {})
        assert "$ref" not in ref_prop

        # The type should be inlined
        assert ref_prop.get("type") == "object"
        assert "properties" in ref_prop
        assert "x" in ref_prop["properties"]

    def test_no_defs_returns_unchanged(self) -> None:
        """Schema without $defs passes through unchanged."""

        class SimpleModel(BaseModel):
            name: str

        schema = TypeAdapter(SimpleModel).json_schema(
            schema_generator=RefResolvingJsonSchemaGenerator
        )

        # Simple model shouldn't have $defs
        assert "$defs" not in schema
        assert schema.get("type") == "object"

    def test_removes_defs_after_resolving(self) -> None:
        """$defs section is removed after refs are resolved."""

        class ReferencedModel(BaseModel):
            value: int

        class ContainerModel(BaseModel):
            ref: ReferencedModel

        schema = TypeAdapter(ContainerModel).json_schema(
            schema_generator=RefResolvingJsonSchemaGenerator
        )

        # $defs should be gone after resolution
        assert "$defs" not in schema

    def test_resolves_nested_refs(self) -> None:
        """References within resolved definitions are also resolved."""

        class DeepModel(BaseModel):
            deep: str

        class MiddleModel(BaseModel):
            middle: DeepModel

        class OuterModel(BaseModel):
            outer: MiddleModel

        schema = TypeAdapter(OuterModel).json_schema(
            schema_generator=RefResolvingJsonSchemaGenerator
        )

        # All refs should be resolved, no $ref or $defs remaining
        schema_str = str(schema)
        assert "$ref" not in schema_str
        assert "$defs" not in schema

    def test_handles_list_of_refs(self) -> None:
        """References in array items are resolved."""

        class ItemModel(BaseModel):
            id: int

        class ContainerModel(BaseModel):
            items: list[ItemModel]

        schema = TypeAdapter(ContainerModel).json_schema(
            schema_generator=RefResolvingJsonSchemaGenerator
        )

        # No $ref should remain
        assert "$ref" not in str(schema)


class TestStrictRefResolvingJsonSchemaGenerator:
    """Test StrictRefResolvingJsonSchemaGenerator combines both transformations."""

    def test_combines_both_transformations(self) -> None:
        """Both strict props and ref resolution are applied."""

        class InnerModel(BaseModel):
            value: int

        class OuterModel(BaseModel):
            inner: InnerModel

        schema = TypeAdapter(OuterModel).json_schema(
            schema_generator=StrictRefResolvingJsonSchemaGenerator
        )

        # Refs should be resolved (no $ref or $defs)
        assert "$ref" not in str(schema)
        assert "$defs" not in schema

        # Root should have additionalProperties: false
        assert schema.get("additionalProperties") is False

        # Inlined inner object should also have additionalProperties: false
        inner_prop = schema.get("properties", {}).get("inner", {})
        assert inner_prop.get("additionalProperties") is False

    def test_with_deeply_nested_models(self) -> None:
        """Works correctly with multiple levels of nesting."""

        class Level3(BaseModel):
            c: str

        class Level2(BaseModel):
            b: Level3

        class Level1(BaseModel):
            a: Level2

        schema = TypeAdapter(Level1).json_schema(
            schema_generator=StrictRefResolvingJsonSchemaGenerator
        )

        # All refs resolved
        assert "$ref" not in str(schema)
        assert "$defs" not in schema

        # All levels have additionalProperties: false
        assert schema.get("additionalProperties") is False

        level2 = schema.get("properties", {}).get("a", {})
        assert level2.get("additionalProperties") is False

        level3 = level2.get("properties", {}).get("b", {})
        assert level3.get("additionalProperties") is False

    def test_with_list_types(self) -> None:
        """Handles list types with nested models correctly."""

        class ItemModel(BaseModel):
            name: str

        class ContainerModel(BaseModel):
            items: list[ItemModel]

        schema = TypeAdapter(ContainerModel).json_schema(
            schema_generator=StrictRefResolvingJsonSchemaGenerator
        )

        # All refs resolved
        assert "$ref" not in str(schema)
        assert "$defs" not in schema

        # Root has additionalProperties: false
        assert schema.get("additionalProperties") is False
