"""Google Embeddings API parameter mappers."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.types import EmbeddingsContent


class OutputDimensionalityMapper(ParameterMapper[EmbeddingsContent]):
    """Map dimensions to Google Embeddings outputDimensionality field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform dimensions into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        for item in request.get("requests", [request]):
            item.setdefault("embedContentConfig", {})["outputDimensionality"] = (
                validated_value
            )

        return request


__all__ = ["OutputDimensionalityMapper"]
