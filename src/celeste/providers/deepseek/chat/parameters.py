"""DeepSeek Chat API parameter mappers."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.types import TextContent


class ThinkingLevelMapper(ParameterMapper[TextContent]):
    """Map thinking_level to DeepSeek's thinking + reasoning_effort fields.

    - "disabled" → thinking={"type": "disabled"}
    - "high"     → thinking={"type": "enabled"}, reasoning_effort="high"
    - "max"      → thinking={"type": "enabled"}, reasoning_effort="max"
    """

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        if validated_value == "disabled":
            request["thinking"] = {"type": "disabled"}
        else:
            request["thinking"] = {"type": "enabled"}
            request["reasoning_effort"] = validated_value
        return request


__all__ = ["ThinkingLevelMapper"]
