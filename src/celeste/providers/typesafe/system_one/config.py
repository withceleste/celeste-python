"""Configuration for TypeSafe System One API."""

from enum import StrEnum


class TypeSafeSystemOneEndpoint(StrEnum):
    """Endpoints for TypeSafe System One API."""

    CREATE_DECISION = "/v1/systemone"


BASE_URL = "https://api.typesafe.ai"

HEADER_TYPESAFE_DANGER_ZONE_IMAGES = "TypeSafe-Danger-Zone-Images"
