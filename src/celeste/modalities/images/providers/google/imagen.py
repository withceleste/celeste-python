"""Imagen client for Google images modality."""

from typing import Any, Unpack

from celeste.artifacts import ImageArtifact
from celeste.mime_types import ImageMimeType
from celeste.parameters import ParameterMapper
from celeste.providers.google.imagen import config as imagen_config
from celeste.providers.google.imagen.client import GoogleImagenClient
from celeste.types import ImageContent

from ...client import ImagesClient
from ...io import ImageInput, ImageOutput
from ...parameters import ImageParameters
from .parameters import IMAGEN_PARAMETER_MAPPERS


class ImagenImagesClient(GoogleImagenClient, ImagesClient):
    """Google Imagen client for images modality (generate)."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[ImageContent]]:
        return IMAGEN_PARAMETER_MAPPERS

    async def generate(
        self,
        prompt: str,
        **parameters: Unpack[ImageParameters],
    ) -> ImageOutput:
        inputs = ImageInput(prompt=prompt)
        return await self._predict(
            inputs,
            endpoint=imagen_config.GoogleImagenEndpoint.CREATE_IMAGE,
            **parameters,
        )

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
            base64_data = prediction.get("bytesBase64Encoded")
            if not base64_data:
                continue
            mime_type = ImageMimeType(prediction.get("mimeType", "image/png"))
            images.append(ImageArtifact(data=base64_data, mime_type=mime_type))

        if len(images) == 1:
            return images[0]
        return images if images else ImageArtifact()

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


__all__ = ["ImagenImagesClient"]
