"""Configuration for BytePlus Images API."""

from enum import StrEnum


class BytePlusImagesEndpoint(StrEnum):
    """Endpoints for BytePlus Images API."""

    CREATE_IMAGE = "/api/v3/images/generations"


BASE_URL = "https://ark.ap-southeast.bytepluses.com"
