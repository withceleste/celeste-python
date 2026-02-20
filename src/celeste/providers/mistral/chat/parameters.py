"""Mistral Chat API parameter mappers."""

from typing import Any, get_args, get_origin

from pydantic import TypeAdapter

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.protocols.chatcompletions.parameters import (
    ResponseFormatMapper as _ResponseFormatMapper,
)
from celeste.structured_outputs import StrictRefResolvingJsonSchemaGenerator


class WebSearchMapper(ParameterMapper):
    """Map web_search to Mistral tools field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform web_search into provider request."""
        validated_value = self._validate_value(value, model)
        if not validated_value:
            return request

        request.setdefault("tools", []).append({"type": "web_search"})
        return request


class ResponseFormatMapper(_ResponseFormatMapper):
    """Map output_schema to Mistral response_format field.

    Handles both single BaseModel and list[BaseModel] types.
    Lists are returned as arrays directly (no wrapping needed).
    """

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform output_schema into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        origin = get_origin(validated_value)
        if origin is list:
            inner_type = get_args(validated_value)[0]
            inner_schema = TypeAdapter(inner_type).json_schema(
                schema_generator=StrictRefResolvingJsonSchemaGenerator,
                mode="serialization",
            )
            schema = {"type": "array", "items": inner_schema}
            name = f"{inner_type.__name__.lower()}_list"
        else:
            schema = TypeAdapter(validated_value).json_schema(
                schema_generator=StrictRefResolvingJsonSchemaGenerator,
                mode="serialization",
            )
            name = validated_value.__name__.lower()

        request["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": name,
                "schema": schema,
                "strict": True,
            },
        }
        return request


__all__ = ["ResponseFormatMapper", "WebSearchMapper"]
