"""Topaz Labs models for images modality."""

from celeste.constraints import Bool, Choice, Constraint, Range
from celeste.core import Modality, Operation, Provider
from celeste.models import Model

from ...parameters import ImageParameter

_OUTPUT_FORMAT = Choice(options=["jpeg", "jpg", "png", "tiff", "tif"])
_OUTPUT_WIDTH = Range(min=1, max=32000)
_OUTPUT_HEIGHT = Range(min=1, max=32000)

_SHARED_ENHANCE_CONSTRAINTS: dict[str, Constraint] = {
    ImageParameter.OUTPUT_FORMAT: _OUTPUT_FORMAT,
    ImageParameter.OUTPUT_WIDTH: _OUTPUT_WIDTH,
    ImageParameter.OUTPUT_HEIGHT: _OUTPUT_HEIGHT,
    ImageParameter.CROP_TO_FILL: Bool(),
    ImageParameter.FACE_ENHANCEMENT: Bool(),
    ImageParameter.FACE_ENHANCEMENT_STRENGTH: Range(min=0.0, max=1.0),
    ImageParameter.FACE_ENHANCEMENT_CREATIVITY: Range(min=0.0, max=1.0),
    ImageParameter.SUBJECT_DETECTION: Choice(
        options=["foreground", "background", "all"]
    ),
    ImageParameter.SHARPEN: Range(min=0.0, max=1.0),
    ImageParameter.DENOISE: Range(min=0.0, max=1.0),
    ImageParameter.FIX_COMPRESSION: Range(min=0.0, max=1.0),
    ImageParameter.STRENGTH: Range(min=0.01, max=1.0),
}

_OUTPUT_ONLY_CONSTRAINTS: dict[str, Constraint] = {
    ImageParameter.OUTPUT_FORMAT: _OUTPUT_FORMAT,
    ImageParameter.OUTPUT_WIDTH: _OUTPUT_WIDTH,
    ImageParameter.OUTPUT_HEIGHT: _OUTPUT_HEIGHT,
    ImageParameter.CROP_TO_FILL: Bool(),
}

MODELS: list[Model] = [
    Model(
        id="Standard V2",
        provider=Provider.TOPAZLABS,
        display_name="Standard 2",
        operations={Modality.IMAGES: {Operation.UPSCALE}},
        parameter_constraints={**_SHARED_ENHANCE_CONSTRAINTS},
    ),
    Model(
        id="High Fidelity V2",
        provider=Provider.TOPAZLABS,
        display_name="High Fidelity 2",
        operations={Modality.IMAGES: {Operation.UPSCALE}},
        parameter_constraints={**_SHARED_ENHANCE_CONSTRAINTS},
    ),
    Model(
        id="Upscale High Fidelity V3",
        provider=Provider.TOPAZLABS,
        display_name="High Fidelity 3",
        operations={Modality.IMAGES: {Operation.UPSCALE}},
        parameter_constraints={
            **_SHARED_ENHANCE_CONSTRAINTS,
            ImageParameter.RECOVERY_STRENGTH: Range(min=0.0, max=1.0),
            ImageParameter.OPACITY: Range(min=0.0, max=1.0),
        },
    ),
    Model(
        id="Low Resolution V2",
        provider=Provider.TOPAZLABS,
        display_name="Low Resolution 2",
        operations={Modality.IMAGES: {Operation.UPSCALE}},
        parameter_constraints={**_SHARED_ENHANCE_CONSTRAINTS},
    ),
    Model(
        id="CGI",
        provider=Provider.TOPAZLABS,
        display_name="Art & CGI",
        operations={Modality.IMAGES: {Operation.UPSCALE}},
        parameter_constraints={
            **_SHARED_ENHANCE_CONSTRAINTS,
            ImageParameter.DEBLUR_STRENGTH: Range(min=0.0, max=1.0),
        },
    ),
    Model(
        id="Transparency Upscale",
        provider=Provider.TOPAZLABS,
        display_name="Transparent Image Upscale",
        operations={Modality.IMAGES: {Operation.UPSCALE}},
        parameter_constraints={
            ImageParameter.OUTPUT_FORMAT: Choice(options=["png"]),
            ImageParameter.OUTPUT_WIDTH: _OUTPUT_WIDTH,
            ImageParameter.OUTPUT_HEIGHT: _OUTPUT_HEIGHT,
            ImageParameter.CROP_TO_FILL: Bool(),
        },
    ),
    Model(
        id="Detail",
        provider=Provider.TOPAZLABS,
        display_name="Detail Faces",
        operations={Modality.IMAGES: {Operation.UPSCALE}},
        parameter_constraints={
            **_OUTPUT_ONLY_CONSTRAINTS,
            ImageParameter.DETAIL_STRENGTH: Range(min=0.0, max=10.0),
        },
    ),
    Model(
        id="Text Refine",
        provider=Provider.TOPAZLABS,
        display_name="Text & Shapes",
        operations={Modality.IMAGES: {Operation.UPSCALE}},
        parameter_constraints={
            **_SHARED_ENHANCE_CONSTRAINTS,
            ImageParameter.DENOISE_STRENGTH: Range(min=0.0, max=1.0),
            ImageParameter.DEBLUR_STRENGTH: Range(min=0.0, max=1.0),
            ImageParameter.DECOMPRESSION_STRENGTH: Range(min=0.0, max=1.0),
            ImageParameter.OPACITY: Range(min=0.0, max=1.0),
        },
    ),
]
