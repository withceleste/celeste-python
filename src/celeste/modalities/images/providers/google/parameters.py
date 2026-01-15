"""Google parameter mappers for images modality."""

from celeste.parameters import ParameterMapper
from celeste.providers.google.generate_content.parameters import (
    AspectRatioMapper as _GeminiAspectRatioMapper,
)
from celeste.providers.google.generate_content.parameters import (
    ImageSizeMapper as _GeminiImageSizeMapper,
)
from celeste.providers.google.generate_content.parameters import (
    MediaContentMapper as _GeminiMediaContentMapper,
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


IMAGEN_PARAMETER_MAPPERS: list[ParameterMapper] = [
    ImagenAspectRatioMapper(),
    ImagenQualityMapper(),
    ImagenNumImagesMapper(),
]


class GeminiAspectRatioMapper(_GeminiAspectRatioMapper):
    """Map aspect_ratio to Gemini generationConfig.imageConfig.aspectRatio."""

    name = ImageParameter.ASPECT_RATIO


class GeminiQualityMapper(_GeminiImageSizeMapper):
    """Map quality to Gemini generationConfig.imageConfig.imageSize."""

    name = ImageParameter.QUALITY


class GeminiReferenceImagesMapper(_GeminiMediaContentMapper):
    """Map reference_images to Gemini contents.parts."""

    name = ImageParameter.REFERENCE_IMAGES


GEMINI_PARAMETER_MAPPERS: list[ParameterMapper] = [
    GeminiAspectRatioMapper(),
    GeminiQualityMapper(),
    GeminiReferenceImagesMapper(),
]


__all__ = [
    "GEMINI_PARAMETER_MAPPERS",
    "IMAGEN_PARAMETER_MAPPERS",
]
