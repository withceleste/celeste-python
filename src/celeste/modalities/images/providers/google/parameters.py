"""Google parameter mappers for images modality."""

from celeste.parameters import ParameterMapper
from celeste.providers.google.generate_content.parameters import (
    AspectRatioMapper as _VertexAspectRatioMapper,
)
from celeste.providers.google.generate_content.parameters import (
    ImageSizeMapper as _VertexImageSizeMapper,
)
from celeste.providers.google.generate_content.parameters import (
    MediaContentMapper as _VertexMediaContentMapper,
)
from celeste.providers.google.generate_content.parameters import (
    ThinkingLevelMapper as _VertexThinkingLevelMapper,
)
from celeste.providers.google.imagen.parameters import (
    AspectRatioMapper as _ImagenAspectRatioMapper,
)
from celeste.providers.google.imagen.parameters import (
    ImageSizeMapper as _ImagenImageSizeMapper,
)
from celeste.providers.google.imagen.parameters import (
    SampleCountMapper as _ImagenSampleCountMapper,
)
from celeste.providers.google.interactions.parameters import (
    AspectRatioMapper as _InteractionsAspectRatioMapper,
)
from celeste.providers.google.interactions.parameters import (
    ImageSizeMapper as _InteractionsImageSizeMapper,
)
from celeste.providers.google.interactions.parameters import (
    MediaContentMapper as _InteractionsMediaContentMapper,
)
from celeste.providers.google.interactions.parameters import (
    ThinkingLevelMapper as _InteractionsThinkingLevelMapper,
)
from celeste.types import ImageContent

from ...parameters import ImageParameter


class ImagenAspectRatioMapper(_ImagenAspectRatioMapper):
    """Map aspect_ratio to Imagen parameters.aspectRatio."""

    name = ImageParameter.ASPECT_RATIO


class ImagenQualityMapper(_ImagenImageSizeMapper):
    """Map quality to Imagen parameters.imageSize."""

    name = ImageParameter.QUALITY


class ImagenNumImagesMapper(_ImagenSampleCountMapper):
    """Map num_images to Imagen parameters.sampleCount."""

    name = ImageParameter.NUM_IMAGES


GOOGLE_IMAGEN_PARAMETER_MAPPERS: list[ParameterMapper[ImageContent]] = [
    ImagenAspectRatioMapper(),
    ImagenQualityMapper(),
    ImagenNumImagesMapper(),
]


class VertexAspectRatioMapper(_VertexAspectRatioMapper[ImageContent]):
    """Map aspect_ratio to Vertex generationConfig.imageConfig.aspectRatio."""

    name = ImageParameter.ASPECT_RATIO


class VertexQualityMapper(_VertexImageSizeMapper[ImageContent]):
    """Map quality to Vertex generationConfig.imageConfig.imageSize."""

    name = ImageParameter.QUALITY


class VertexReferenceImagesMapper(_VertexMediaContentMapper[ImageContent]):
    """Map reference_images to Vertex contents.parts."""

    name = ImageParameter.REFERENCE_IMAGES


class VertexThinkingLevelMapper(_VertexThinkingLevelMapper[ImageContent]):
    """Map thinking_level to Vertex generationConfig.thinkingConfig.thinkingLevel."""

    name = ImageParameter.THINKING_LEVEL


GOOGLE_VERTEX_PARAMETER_MAPPERS: list[ParameterMapper[ImageContent]] = [
    VertexAspectRatioMapper(),
    VertexQualityMapper(),
    VertexReferenceImagesMapper(),
    VertexThinkingLevelMapper(),
]


class InteractionsAspectRatioMapper(_InteractionsAspectRatioMapper):
    """Map aspect_ratio to Google Interactions response_format.aspect_ratio."""

    name = ImageParameter.ASPECT_RATIO


class InteractionsQualityMapper(_InteractionsImageSizeMapper):
    """Map quality to Google Interactions response_format.image_size."""

    name = ImageParameter.QUALITY


class InteractionsReferenceImagesMapper(_InteractionsMediaContentMapper[ImageContent]):
    """Map reference_images to Google Interactions input content."""

    name = ImageParameter.REFERENCE_IMAGES


class InteractionsThinkingLevelMapper(_InteractionsThinkingLevelMapper[ImageContent]):
    """Map thinking_level to Google Interactions generation_config.thinking_level."""

    name = ImageParameter.THINKING_LEVEL


GOOGLE_INTERACTIONS_PARAMETER_MAPPERS: list[ParameterMapper[ImageContent]] = [
    InteractionsAspectRatioMapper(),
    InteractionsQualityMapper(),
    InteractionsReferenceImagesMapper(),
    InteractionsThinkingLevelMapper(),
]


__all__ = [
    "GOOGLE_IMAGEN_PARAMETER_MAPPERS",
    "GOOGLE_INTERACTIONS_PARAMETER_MAPPERS",
    "GOOGLE_VERTEX_PARAMETER_MAPPERS",
]
