"""Utility functions for Celeste."""

import base64

from celeste.artifacts import ImageArtifact


def image_to_data_uri(image: ImageArtifact) -> str:
    """Convert an ImageArtifact to a base64 data URI string.

    Args:
        image: ImageArtifact with data or path.

    Returns:
        Data URI string (e.g., "data:image/png;base64,iVBORw0KGgo...").

    Raises:
        ValueError: If image has neither data nor path.
    """
    if image.data:
        file_data = image.data
    elif image.path:
        with open(image.path, "rb") as f:
            file_data = f.read()
    else:
        msg = "ImageArtifact must have data or path"
        raise ValueError(msg)

    base64_data = base64.b64encode(file_data).decode("utf-8")
    mime_type = image.mime_type.value if image.mime_type else "image/jpeg"

    return f"data:{mime_type};base64,{base64_data}"


__all__ = ["image_to_data_uri"]
