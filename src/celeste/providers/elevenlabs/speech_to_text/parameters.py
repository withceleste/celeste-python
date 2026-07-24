"""ElevenLabs Speech-to-Text API parameter mappers."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper


class LanguageCodeMapper[Content](ParameterMapper[Content]):
    """Map language to ElevenLabs language_code field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform language into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request
        request["language_code"] = validated_value
        return request


__all__ = [
    "LanguageCodeMapper",
]
