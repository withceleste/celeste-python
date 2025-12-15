"""BFL Images API utilities."""

import base64

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


__all__ = ["encode_image"]
