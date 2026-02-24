"""HuggingFace Chat API parameter mappers."""

from typing import Any, get_args, get_origin

from pydantic import TypeAdapter

from celeste.models import Model
from celeste.protocols.chatcompletions.parameters import (
    ResponseFormatMapper as _ResponseFormatMapper,
)
from celeste.structured_outputs import StrictJsonSchemaGenerator


class ResponseFormatMapper(_ResponseFormatMapper):
    """Map output_schema to HuggingFace response_format field (json_schema mode).

    Handles both single BaseModel and list[BaseModel] types.
    HuggingFace requires top-level object, so lists are wrapped in {items: []}.
    Uses json_schema mode with strict: true.
    """

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform output_schema into HuggingFace response_format."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        origin = get_origin(validated_value)
        if origin is list:
            # HuggingFace requires top-level object, wrap list in {"items": [...]}
            inner_type = get_args(validated_value)[0]
            inner_schema = TypeAdapter(inner_type).json_schema(
                schema_generator=StrictJsonSchemaGenerator,
                mode="serialization",
            )
            schema = {
                "type": "object",
                "properties": {"items": {"type": "array", "items": inner_schema}},
                "required": ["items"],
            }
            name = f"{inner_type.__name__.lower()}_list"
        else:
            schema = TypeAdapter(validated_value).json_schema(
                schema_generator=StrictJsonSchemaGenerator,
                mode="serialization",
            )
            name = validated_value.__name__.lower()

        request["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": name,
                "strict": True,
                "schema": schema,
            },
        }
        return request


__all__ = ["ResponseFormatMapper"]
