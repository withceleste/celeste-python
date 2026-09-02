"""BFL Images API utilities."""

from typing import Any

from celeste.artifacts import ImageArtifact
from celeste.providers.bfl.utils import encode_artifact


def encode_image(image: ImageArtifact) -> str:
    """Encode ImageArtifact to base64 string or return URL.

    BFL API accepts either a URL or base64-encoded image data.
    """
    return encode_artifact(image)


def add_reference_images(
    request: dict[str, Any],
    images: list[ImageArtifact],
) -> dict[str, Any]:
    """Add reference images to a BFL request dict.

    Generation starts at ``input_image``; editing reserves that field for the
    primary image and starts references at ``input_image_2``.
    """
    start = 2 if "input_image" in request else 1
    for index, image in enumerate(images, start=start):
        name = "input_image" if index == 1 else f"input_image_{index}"
        request[name] = encode_image(image)
    return request


__all__ = ["add_reference_images", "encode_image"]
