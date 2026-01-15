"""Google Embeddings API parameter mappers."""

from typing import Any

from celeste.models import Model
from celeste.parameters import ParameterMapper


class OutputDimensionalityMapper(ParameterMapper):
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

        # Batch request: add to each individual request
        if "requests" in request:
            for req in request["requests"]:
                req["outputDimensionality"] = validated_value
        else:
            # Single request: add at root level
            request["outputDimensionality"] = validated_value

        return request


__all__ = ["OutputDimensionalityMapper"]
