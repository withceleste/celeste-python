"""Imagen client for Google images modality."""

from typing import Any, Unpack

from celeste.artifacts import ImageArtifact
from celeste.mime_types import ImageMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.google.auth import GoogleADC
from celeste.providers.google.imagen import config
from celeste.providers.google.imagen.client import (
    GoogleImagenClient as GoogleImagenMixin,
)
from celeste.types import ImageContent

from ...client import ImagesClient
from ...io import ImageInput
from ...parameters import ImageParameters
from .parameters import (
    GOOGLE_IMAGEN_PARAMETER_MAPPERS,
    GOOGLE_IMAGEN_UPSCALE_PARAMETER_MAPPERS,
)


class GoogleImagenImagesClient(GoogleImagenMixin, ImagesClient):
    """Google Imagen client for images modality (generate)."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[ImageContent]]:
        return GOOGLE_IMAGEN_PARAMETER_MAPPERS

    def _init_request(self, inputs: ImageInput) -> dict[str, Any]:
        """Initialize request for Imagen API."""
        return {
            "instances": [{"prompt": inputs.prompt}],
            "parameters": {},
        }

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> ImageContent:
        """Parse image artifacts from Imagen predictions."""
        predictions = super()._parse_content(response_data)

        images: list[ImageArtifact] = []
        for prediction in predictions:
            if not self._is_image_prediction(prediction):
                continue
            base64_data = prediction.get("bytesBase64Encoded")
            mime_type = ImageMimeType(prediction.get("mimeType", "image/png"))
            images.append(ImageArtifact(data=base64_data, mime_type=mime_type))

        if len(images) == 1:
            return images[0]
        return images

    def _transform_output(
        self,
        content: ImageContent,
        **parameters: Unpack[ImageParameters],
    ) -> ImageContent:
        """Singularize/pluralize based on num_images parameter."""
        content = super()._transform_output(content, **parameters)
        num_images_requested = parameters.get("num_images")
        if num_images_requested == 1 and isinstance(content, list):
            return content[0] if content else ImageArtifact()
        if (
            num_images_requested is not None
            and num_images_requested > 1
            and not isinstance(content, list)
        ):
            return [content]
        return content


class GoogleImagenUpscaleImagesClient(GoogleImagenImagesClient):
    """Imagen 4 upscaling client on Vertex AI."""

    _upscale_endpoint = config.GoogleImagenEndpoint.CREATE_IMAGE

    def model_post_init(self, __context: object) -> None:
        """Require the Cloud-only regional Vertex AI serving route."""
        super().model_post_init(__context)
        if not isinstance(self.auth, GoogleADC):
            raise ValueError("Imagen 4 upscaling requires GoogleADC authentication")
        if self.auth.location == "global":
            raise ValueError(
                "Imagen 4 upscaling requires a regional GoogleADC location"
            )

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[ImageContent]]:
        return GOOGLE_IMAGEN_UPSCALE_PARAMETER_MAPPERS

    def _init_request(self, inputs: ImageInput) -> dict[str, Any]:
        """Build an Imagen upscale Predict request."""
        image = inputs.image
        if image is None:
            raise ValueError("Imagen 4 upscaling requires an input image")

        if image.url:
            if not image.url.startswith("gs://"):
                raise ValueError("Imagen 4 upscaling image URLs must use gs://")
            image_data = {"gcsUri": image.url}
        else:
            image_data = {"bytesBase64Encoded": image.get_base64()}

        return {
            "instances": [{"prompt": "Upscale the image", "image": image_data}],
            "parameters": {"mode": "upscale"},
        }

    def _build_request(
        self,
        inputs: ImageInput,
        **parameters: Unpack[ImageParameters],
    ) -> dict[str, Any]:
        """Require the provider's mandatory upscale factor."""
        if parameters.get("upscale_factor") is None:
            raise ValueError("Imagen 4 upscaling requires upscale_factor")
        return super()._build_request(inputs, **parameters)


__all__ = ["GoogleImagenImagesClient", "GoogleImagenUpscaleImagesClient"]
