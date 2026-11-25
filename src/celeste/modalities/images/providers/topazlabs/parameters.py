"""Topaz Labs parameter mappers for images modality."""

from celeste.parameters import ParameterMapper
from celeste.providers.topazlabs.image.parameters import (
    CropToFillMapper as _CropToFillMapper,
    DeblurStrengthMapper as _DeblurStrengthMapper,
    DecompressionStrengthMapper as _DecompressionStrengthMapper,
    DenoiseMapper as _DenoiseMapper,
    DenoiseStrengthMapper as _DenoiseStrengthMapper,
    DetailStrengthMapper as _DetailStrengthMapper,
    FaceEnhancementCreativityMapper as _FaceEnhancementCreativityMapper,
    FaceEnhancementMapper as _FaceEnhancementMapper,
    FaceEnhancementStrengthMapper as _FaceEnhancementStrengthMapper,
    FixCompressionMapper as _FixCompressionMapper,
    OpacityMapper as _OpacityMapper,
    OutputFormatMapper as _OutputFormatMapper,
    OutputHeightMapper as _OutputHeightMapper,
    OutputWidthMapper as _OutputWidthMapper,
    RecoveryStrengthMapper as _RecoveryStrengthMapper,
    SharpenMapper as _SharpenMapper,
    StrengthMapper as _StrengthMapper,
    SubjectDetectionMapper as _SubjectDetectionMapper,
)
from celeste.types import ImageContent

from ...parameters import ImageParameter


class OutputWidthMapper(_OutputWidthMapper):
    name = ImageParameter.OUTPUT_WIDTH


class OutputHeightMapper(_OutputHeightMapper):
    name = ImageParameter.OUTPUT_HEIGHT


class OutputFormatMapper(_OutputFormatMapper):
    name = ImageParameter.OUTPUT_FORMAT


class CropToFillMapper(_CropToFillMapper):
    name = ImageParameter.CROP_TO_FILL


class FaceEnhancementMapper(_FaceEnhancementMapper):
    name = ImageParameter.FACE_ENHANCEMENT


class FaceEnhancementStrengthMapper(_FaceEnhancementStrengthMapper):
    name = ImageParameter.FACE_ENHANCEMENT_STRENGTH


class FaceEnhancementCreativityMapper(_FaceEnhancementCreativityMapper):
    name = ImageParameter.FACE_ENHANCEMENT_CREATIVITY


class SubjectDetectionMapper(_SubjectDetectionMapper):
    name = ImageParameter.SUBJECT_DETECTION


class SharpenMapper(_SharpenMapper):
    name = ImageParameter.SHARPEN


class DenoiseMapper(_DenoiseMapper):
    name = ImageParameter.DENOISE


class StrengthMapper(_StrengthMapper):
    name = ImageParameter.STRENGTH


class FixCompressionMapper(_FixCompressionMapper):
    name = ImageParameter.FIX_COMPRESSION


class RecoveryStrengthMapper(_RecoveryStrengthMapper):
    name = ImageParameter.RECOVERY_STRENGTH


class OpacityMapper(_OpacityMapper):
    name = ImageParameter.OPACITY


class DeblurStrengthMapper(_DeblurStrengthMapper):
    name = ImageParameter.DEBLUR_STRENGTH


class DetailStrengthMapper(_DetailStrengthMapper):
    name = ImageParameter.DETAIL_STRENGTH


class DenoiseStrengthMapper(_DenoiseStrengthMapper):
    name = ImageParameter.DENOISE_STRENGTH


class DecompressionStrengthMapper(_DecompressionStrengthMapper):
    name = ImageParameter.DECOMPRESSION_STRENGTH


TOPAZLABS_PARAMETER_MAPPERS: list[ParameterMapper[ImageContent]] = [
    OutputWidthMapper(),
    OutputHeightMapper(),
    OutputFormatMapper(),
    CropToFillMapper(),
    FaceEnhancementMapper(),
    FaceEnhancementStrengthMapper(),
    FaceEnhancementCreativityMapper(),
    SubjectDetectionMapper(),
    SharpenMapper(),
    DenoiseMapper(),
    StrengthMapper(),
    FixCompressionMapper(),
    RecoveryStrengthMapper(),
    OpacityMapper(),
    DeblurStrengthMapper(),
    DetailStrengthMapper(),
    DenoiseStrengthMapper(),
    DecompressionStrengthMapper(),
]

__all__ = ["TOPAZLABS_PARAMETER_MAPPERS"]
