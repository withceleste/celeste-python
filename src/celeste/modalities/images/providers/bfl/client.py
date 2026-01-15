"""BFL images client."""

from typing import Any, Unpack

from celeste.artifacts import ImageArtifact
from celeste.parameters import ParameterMapper
from celeste.providers.bfl.images import config as bfl_config
from celeste.providers.bfl.images.client import BFLImagesClient as _BFLImagesClient
from celeste.providers.bfl.images.utils import encode_image

from ...client import ImagesClient
from ...io import ImageFinishReason, ImageInput, ImageOutput, ImageUsage
from ...parameters import ImageParameters
from .parameters import BFL_PARAMETER_MAPPERS


class BFLImagesClient(_BFLImagesClient, ImagesClient):
    """BFL images client (generate + edit)."""

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper]:
        return BFL_PARAMETER_MAPPERS

    async def generate(
        self,
        prompt: str,
        **parameters: Unpack[ImageParameters],
    ) -> ImageOutput:
        """Generate images from prompt."""
        inputs = ImageInput(prompt=prompt)
        return await self._predict(
            inputs,
            endpoint=bfl_config.BFLImagesEndpoint.CREATE_IMAGE,
            **parameters,
        )

    async def edit(
        self,
        image: ImageArtifact,
        prompt: str,
        **parameters: Unpack[ImageParameters],
    ) -> ImageOutput:
        """Edit an image with a prompt."""
        inputs = ImageInput(prompt=prompt, image=image)
        return await self._predict(
            inputs,
            endpoint=bfl_config.BFLImagesEndpoint.CREATE_IMAGE,
            **parameters,
        )

    def _init_request(self, inputs: ImageInput) -> dict[str, Any]:
        """Build request with prompt and (optional) input image."""
        request: dict[str, Any] = {"prompt": inputs.prompt}
        if inputs.image is not None:
            request["input_image"] = encode_image(inputs.image)
        return request

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
        result = super()._parse_content(response_data)
        sample_url = result.get("sample")

        if not sample_url:
            msg = f"No image URL in {self.provider} response"
            raise ValueError(msg)

        return ImageArtifact(url=sample_url)

    def _parse_finish_reason(self, response_data: dict[str, Any]) -> ImageFinishReason:
        """Parse finish reason from response."""
        status = response_data.get("status")
        if status == "Ready":
            return ImageFinishReason(reason="COMPLETE")
        elif status in ("Error", "Failed"):
            error_msg = response_data.get("error", "Edit failed")
            return ImageFinishReason(reason="ERROR", message=error_msg)
        return ImageFinishReason(reason=None)


__all__ = ["BFLImagesClient"]
