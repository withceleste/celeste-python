"""BFL Images API utilities."""

import base64
from typing import Any

from celeste.artifacts import ImageArtifact

from .config import BFLImageField, image_field_for_model


def encode_image(image: ImageArtifact) -> str:
    """Encode ImageArtifact to base64 string or return URL.

    BFL API accepts either a URL or base64-encoded image data.
    """
    if image.url:
        return image.url
    elif image.data:
        if isinstance(image.data, bytes):
            return base64.b64encode(image.data).decode("utf-8")
        return image.data
    elif image.path:
        with open(image.path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    else:
        msg = "ImageArtifact must have url, data, or path"
        raise ValueError(msg)


def add_input_images(
    request: dict[str, Any],
    images: list[ImageArtifact],
    model_id: str,
) -> dict[str, Any]:
    """Add input images to a BFL request dict after any already placed.

    The model's image field decides the layout: ``images`` is one list, other
    fields start at their own name and number later images ``<field>_2``, ...
    """
    if not images:
        return request
    field = image_field_for_model(model_id).value
    encoded = [encode_image(image) for image in images]
    if field == BFLImageField.IMAGES:
        request[field] = [*request.get(field, []), *encoded]
        return request
    start = 2 if field in request else 1
    for index, value in enumerate(encoded, start=start):
        request[field if index == 1 else f"{field}_{index}"] = value
    return request


__all__ = ["add_input_images", "encode_image"]
