"""Configuration for BytePlus Images API."""

from enum import StrEnum


class BytePlusImagesEndpoint(StrEnum):
    """Endpoints for BytePlus Images API."""

    CREATE_IMAGE = "/images/generations"


BASE_URL = "https://ark.ap-southeast.bytepluses.com/api/v3"
