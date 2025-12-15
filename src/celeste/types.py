"""Type definitions for Celeste."""

from pydantic import BaseModel

type JsonValue = (
    str | int | float | bool | None | dict[str, JsonValue] | list[JsonValue]
)

type StructuredOutput = str | JsonValue | BaseModel | list[BaseModel]

__all__ = ["JsonValue", "StructuredOutput"]
