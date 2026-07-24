"""Topaz Labs Image API parameter mappers."""

from celeste.parameters import FieldMapper
from celeste.types import ImageContent


class OutputWidthMapper(FieldMapper[ImageContent]):
    """Map output_width to Topaz output_width field."""

    field = "output_width"


class OutputHeightMapper(FieldMapper[ImageContent]):
    """Map output_height to Topaz output_height field."""

    field = "output_height"


class OutputFormatMapper(FieldMapper[ImageContent]):
    """Map output_format to Topaz output_format field."""

    field = "output_format"


class CropToFillMapper(FieldMapper[ImageContent]):
    """Map crop_to_fill to Topaz crop_to_fill field."""

    field = "crop_to_fill"


class FaceEnhancementMapper(FieldMapper[ImageContent]):
    """Map face_enhancement to Topaz face_enhancement field."""

    field = "face_enhancement"


class FaceEnhancementStrengthMapper(FieldMapper[ImageContent]):
    """Map face_enhancement_strength to Topaz face_enhancement_strength field."""

    field = "face_enhancement_strength"


class FaceEnhancementCreativityMapper(FieldMapper[ImageContent]):
    """Map face_enhancement_creativity to Topaz face_enhancement_creativity field."""

    field = "face_enhancement_creativity"


class SubjectDetectionMapper(FieldMapper[ImageContent]):
    """Map subject_detection to Topaz subject_detection field."""

    field = "subject_detection"


class SharpenMapper(FieldMapper[ImageContent]):
    """Map sharpen to Topaz sharpen field."""

    field = "sharpen"


class DenoiseMapper(FieldMapper[ImageContent]):
    """Map denoise to Topaz denoise field."""

    field = "denoise"


class StrengthMapper(FieldMapper[ImageContent]):
    """Map strength to Topaz strength field."""

    field = "strength"


class FixCompressionMapper(FieldMapper[ImageContent]):
    """Map fix_compression to Topaz fix_compression field."""

    field = "fix_compression"


class RecoveryStrengthMapper(FieldMapper[ImageContent]):
    """Map recovery_strength to Topaz recovery_strength field."""

    field = "recovery_strength"


class OpacityMapper(FieldMapper[ImageContent]):
    """Map opacity to Topaz opacity field."""

    field = "opacity"


class DeblurStrengthMapper(FieldMapper[ImageContent]):
    """Map deblur_strength to Topaz deblur_strength field."""

    field = "deblur_strength"


class DetailStrengthMapper(FieldMapper[ImageContent]):
    """Map detail_strength to Topaz detail_strength field."""

    field = "detail_strength"


class DenoiseStrengthMapper(FieldMapper[ImageContent]):
    """Map denoise_strength to Topaz denoise_strength field."""

    field = "denoise_strength"


class DecompressionStrengthMapper(FieldMapper[ImageContent]):
    """Map decompression_strength to Topaz decompression_strength field."""

    field = "decompression_strength"


__all__ = [
    "CropToFillMapper",
    "DeblurStrengthMapper",
    "DecompressionStrengthMapper",
    "DenoiseMapper",
    "DenoiseStrengthMapper",
    "DetailStrengthMapper",
    "FaceEnhancementCreativityMapper",
    "FaceEnhancementMapper",
    "FaceEnhancementStrengthMapper",
    "FixCompressionMapper",
    "OpacityMapper",
    "OutputFormatMapper",
    "OutputHeightMapper",
    "OutputWidthMapper",
    "RecoveryStrengthMapper",
    "SharpenMapper",
    "StrengthMapper",
    "SubjectDetectionMapper",
]
