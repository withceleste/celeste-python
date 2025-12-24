"""Celeste video generation capability."""


def register_package() -> None:
    """Register video generation package (client, models, and input)."""
    from celeste.client import register_client
    from celeste.core import Capability
    from celeste.io import register_input
    from celeste.models import register_models
    from celeste_video_generation.io import VideoGenerationInput
    from celeste_video_generation.models import MODELS
    from celeste_video_generation.providers import PROVIDERS

    for provider, client_class in PROVIDERS:
        register_client(Capability.VIDEO_GENERATION, provider, client_class)

    register_models(MODELS, capability=Capability.VIDEO_GENERATION)
    register_input(Capability.VIDEO_GENERATION, VideoGenerationInput)


from celeste_video_generation.io import (  # noqa: E402
    VideoGenerationInput,
    VideoGenerationOutput,
    VideoGenerationUsage,
)

__all__ = [
    "VideoGenerationInput",
    "VideoGenerationOutput",
    "VideoGenerationUsage",
    "register_package",
]
