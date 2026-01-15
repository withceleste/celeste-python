"""BFL Images API utilities."""

import base64
from typing import Any

from celeste.artifacts import ImageArtifact


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


def add_reference_images(
    request: dict[str, Any],
    images: list[ImageArtifact],
    *,
    start_index: int = 2,
) -> dict[str, Any]:
    """Add additional reference images to a BFL request dict.

    BFL expects extra images as sequential fields: ``input_image_2``,
    ``input_image_3``, ...
    """
    for i, image in enumerate(images, start=start_index):
        request[f"input_image_{i}"] = encode_image(image)
    return request


__all__ = ["add_reference_images", "encode_image"]
