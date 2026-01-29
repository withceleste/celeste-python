"""xAI images client."""

from typing import Any, Unpack

from celeste.artifacts import ImageArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.xai.images import config
from celeste.providers.xai.images.client import XAIImagesClient as XAIImagesMixin

from ...client import ImagesClient
from ...io import (
    ImageFinishReason,
    ImageInput,
    ImageOutput,
    ImageUsage,
)
from ...parameters import ImageParameters
from .parameters import XAI_PARAMETER_MAPPERS


class XAIImagesClient(XAIImagesMixin, ImagesClient):
    """xAI images client."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return XAI_PARAMETER_MAPPERS

    def _init_request(self, inputs: ImageInput) -> dict[str, Any]:
        """Initialize request from inputs."""
        request: dict[str, Any] = {"prompt": inputs.prompt}
        if inputs.image is not None:
            # xAI expects {"image": {"url": "..."}} with URL or data URI
            if inputs.image.url:
                request["image"] = {"url": inputs.image.url}
            else:
                mime_type = inputs.image.mime_type
                base64_data = inputs.image.get_base64()
                request["image"] = {"url": f"data:{mime_type};base64,{base64_data}"}
        return request

    async def generate(
        self,
        prompt: str,
        **parameters: Unpack[ImageParameters],
    ) -> ImageOutput:
        """Generate images from prompt."""
        inputs = ImageInput(prompt=prompt)
        return await self._predict(
            inputs,
            endpoint=config.XAIImagesEndpoint.CREATE_IMAGE,
            **parameters,
        )

    async def edit(
        self,
        image: ImageArtifact,
        prompt: str,
        **parameters: Unpack[ImageParameters],
    ) -> ImageOutput:
        """Edit an image with text instructions."""
        inputs = ImageInput(image=image, prompt=prompt)
        return await self._predict(
            inputs,
            endpoint=config.XAIImagesEndpoint.CREATE_EDIT,
            **parameters,
        )

    def _parse_usage(self, response_data: dict[str, Any]) -> ImageUsage:
        """Parse usage from response."""
        usage = super()._parse_usage(response_data)
        return ImageUsage(**usage)

    def _parse_content(
        self,
        response_data: dict[str, Any],
        **parameters: Unpack[ImageParameters],
    ) -> ImageArtifact:
        """Parse content from response."""
        data = super()._parse_content(response_data)
        image_data = data[0]

        # xAI returns either b64_json or url
        b64_json = image_data.get("b64_json")
        if b64_json:
            import base64

            image_bytes = base64.b64decode(b64_json)
            return ImageArtifact(data=image_bytes)

        url = image_data.get("url")
        if url:
            return ImageArtifact(url=url)

        msg = "No image URL or base64 data in response"
        raise ValueError(msg)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> ImageFinishReason:
        """Parse finish reason from response."""
        finish_reason = super()._parse_finish_reason(response_data)
        return ImageFinishReason(reason=finish_reason.reason)


__all__ = ["XAIImagesClient"]
