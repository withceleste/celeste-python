"""Configuration for BFL Images API."""

from enum import StrEnum


class BFLImagesEndpoint(StrEnum):
    """Endpoints for BFL Images API."""

    CREATE_IMAGE = "/v1/{model_id}"


class BFLImageField(StrEnum):
    """Request fields that carry input images on BFL image endpoints."""

    INPUT_IMAGE = "input_image"
    IMAGES = "images"
    IMAGE_PROMPT = "image_prompt"


# Model id → field carrying input images, from each endpoint's request schema.
# images is one list; input_image continues as input_image_2, input_image_3, ...;
# image_prompt takes one image. Counts are REFERENCE_IMAGES catalog constraints.
IMAGE_FIELD_BY_MODEL: dict[str, BFLImageField] = {
    "flux-3-image": BFLImageField.IMAGES,
    "flux-2-max": BFLImageField.INPUT_IMAGE,
    "flux-2-pro": BFLImageField.INPUT_IMAGE,
    "flux-2-pro-preview": BFLImageField.INPUT_IMAGE,
    "flux-2-klein-4b": BFLImageField.INPUT_IMAGE,
    "flux-2-klein-9b": BFLImageField.INPUT_IMAGE,
    "flux-2-klein-9b-preview": BFLImageField.INPUT_IMAGE,
    "flux-2-flex": BFLImageField.INPUT_IMAGE,
    "flux-kontext-max": BFLImageField.INPUT_IMAGE,
    "flux-kontext-pro": BFLImageField.INPUT_IMAGE,
    "flux-pro-1.1-ultra": BFLImageField.IMAGE_PROMPT,
    "flux-pro-1.1": BFLImageField.IMAGE_PROMPT,
    "flux-dev": BFLImageField.IMAGE_PROMPT,
}


def image_field_for_model(model_id: str) -> BFLImageField:
    """Resolve the input image field for a catalogued BFL model id."""
    try:
        return IMAGE_FIELD_BY_MODEL[model_id]
    except KeyError:
        msg = f"No BFL input image field for model id: {model_id!r}"
        raise KeyError(msg) from None


BASE_URL = "https://api.bfl.ai"

# Polling Configuration
POLLING_INTERVAL = 0.5  # seconds between polling attempts
POLLING_TIMEOUT = 120.0  # 2 minutes timeout
