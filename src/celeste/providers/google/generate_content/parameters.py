"""Google GenerateContent API parameter mappers."""

import base64
import json
from typing import Any, get_args, get_origin

from pydantic import BaseModel, TypeAdapter

from celeste.artifacts import ImageArtifact
from celeste.mime_types import ApplicationMimeType
from celeste.models import Model
from celeste.parameters import ParameterMapper
from celeste.types import TextContent


class TemperatureMapper(ParameterMapper):
    """Map temperature to Google generationConfig.temperature field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform temperature into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request.setdefault("generationConfig", {})["temperature"] = validated_value
        return request


class MaxOutputTokensMapper(ParameterMapper):
    """Map max_tokens to Google generationConfig.maxOutputTokens field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform max_tokens into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request.setdefault("generationConfig", {})["maxOutputTokens"] = validated_value
        return request


class ThinkingBudgetMapper(ParameterMapper):
    """Map thinkingBudget to Google generationConfig.thinkingConfig.thinkingBudget field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform thinkingBudget into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request.setdefault("generationConfig", {}).setdefault("thinkingConfig", {})[
            "thinkingBudget"
        ] = validated_value
        return request


class ThinkingLevelMapper(ParameterMapper):
    """Map thinkingLevel to Google generationConfig.thinkingConfig.thinkingLevel field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform thinkingLevel into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request.setdefault("generationConfig", {}).setdefault("thinkingConfig", {})[
            "thinkingLevel"
        ] = validated_value
        return request


class AspectRatioMapper(ParameterMapper):
    """Map aspect_ratio to Google generationConfig.imageConfig.aspectRatio field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform aspect_ratio into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request.setdefault("generationConfig", {}).setdefault("imageConfig", {})[
            "aspectRatio"
        ] = validated_value
        return request


class ImageSizeMapper(ParameterMapper):
    """Map image_size to Google generationConfig.imageConfig.imageSize field."""

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform image_size into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        request.setdefault("generationConfig", {}).setdefault("imageConfig", {})[
            "imageSize"
        ] = validated_value
        return request


class MediaContentMapper(ParameterMapper):
    """Map reference_images to Google contents.parts field."""

    def _build_image_part(self, image: ImageArtifact) -> dict[str, Any]:
        """Build a Gemini part from an ImageArtifact."""
        if image.url:
            return {"file_data": {"file_uri": image.url}}

        if image.data:
            b64 = (
                base64.b64encode(image.data).decode("utf-8")
                if isinstance(image.data, bytes)
                else image.data
            )
            return {"inline_data": {"mime_type": str(image.mime_type), "data": b64}}

        if image.path:
            with open(image.path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            return {"inline_data": {"mime_type": str(image.mime_type), "data": b64}}

        msg = "ImageArtifact must have url, data, or path"
        raise ValueError(msg)

    def map(
        self,
        request: dict[str, Any],
        value: object,
        model: Model,
    ) -> dict[str, Any]:
        """Transform reference_images into provider request."""
        validated_value = self._validate_value(value, model)
        if validated_value is None:
            return request

        # Convert list of ImageArtifact to list of image parts
        image_parts = [self._build_image_part(img) for img in validated_value]

        # Add image parts before text in contents[0].parts
        if "contents" in request and len(request["contents"]) > 0:
            parts = request["contents"][0].get("parts", [])
            # Find text part and insert images before it
            text_index = next(
                (i for i, part in enumerate(parts) if "text" in part), len(parts)
            )
            # Insert image parts before text
            parts[text_index:text_index] = image_parts
            request["contents"][0]["parts"] = parts

        return request


class WebSearchMapper(ParameterMapper):
    """Map web_search to Google tools field."""

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

        request["tools"] = [{"google_search": {}}]
        return request


class ResponseJsonSchemaMapper(ParameterMapper):
    """Map output_schema to Google generationConfig.responseJsonSchema field."""

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

        schema = self._convert_to_google_schema(validated_value)

        config = request.setdefault("generationConfig", {})
        config["responseJsonSchema"] = schema
        config["responseMimeType"] = ApplicationMimeType.JSON

        return request

    def parse_output(self, content: TextContent, value: object | None) -> TextContent:
        """Parse JSON to BaseModel using Pydantic's TypeAdapter."""
        if value is None:
            return content

        # If content is already a BaseModel, return it unchanged
        if isinstance(content, BaseModel):
            return content
        if isinstance(content, list) and content and isinstance(content[0], BaseModel):
            return content

        parsed = json.loads(content) if isinstance(content, str) else content

        # For list[T], handle various formats Google might return
        origin = get_origin(value)
        if origin is list and isinstance(parsed, dict):
            # Google returns arrays directly in JSON schema, but might wrap in object
            if "items" in parsed:
                parsed = parsed["items"]
            else:
                # If it's a dict but not wrapped, try to extract array values
                parsed = list(parsed.values()) if parsed else []

        return TypeAdapter(value).validate_python(parsed)

    def _convert_to_google_schema(self, output_schema: Any) -> dict[str, Any]:  # noqa: ANN401
        """Convert Pydantic BaseModel or list[BaseModel] to Google JSON Schema format."""
        origin = get_origin(output_schema)
        if origin is list:
            inner_type = get_args(output_schema)[0]
            items_schema = inner_type.model_json_schema()
            defs = items_schema.get("$defs", {})
            items_schema_clean = {k: v for k, v in items_schema.items() if k != "$defs"}
            json_schema = {"type": "array", "items": items_schema_clean}
            if defs:
                json_schema["$defs"] = defs
        else:
            json_schema = output_schema.model_json_schema()

        json_schema = self._remove_unsupported_fields(json_schema)
        return json_schema

    def _remove_unsupported_fields(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Remove unsupported metadata fields from schema."""
        result: dict[str, Any] = {}

        for key, value in schema.items():
            if key == "title":
                continue

            if isinstance(value, dict):
                result[key] = self._remove_unsupported_fields(value)
            elif isinstance(value, list):
                result[key] = [
                    self._remove_unsupported_fields(item)
                    if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                result[key] = value

        return result


__all__ = [
    "AspectRatioMapper",
    "ImageSizeMapper",
    "MaxOutputTokensMapper",
    "MediaContentMapper",
    "ResponseJsonSchemaMapper",
    "TemperatureMapper",
    "ThinkingBudgetMapper",
    "ThinkingLevelMapper",
    "WebSearchMapper",
]
