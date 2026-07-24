"""fal segmentation client."""

from typing import Any, ClassVar

from celeste.parameters import ParameterMapper
from celeste.providers.fal.queue import config
from celeste.providers.fal.queue.client import FalQueueClient as FalQueueMixin
from celeste.types import SegmentationContent, SegmentationMask
from celeste.utils.mime import build_data_url

from ...client import SegmentationClient
from ...io import SegmentationInput
from .parameters import FAL_PARAMETER_MAPPERS


class FalSegmentationClient(FalQueueMixin, SegmentationClient):
    """fal segmentation client."""

    _segment_endpoint = config.FalQueueEndpoint.RUN
    _content_fields: ClassVar[set[str]] = {
        "rle",
        "scores",
        "boxes",
        "metadata",
        "boundingbox_frames_zip",
    }

    @classmethod
    def parameter_mappers(cls) -> list[ParameterMapper[SegmentationContent]]:
        """Return parameter mappers for fal segmentation."""
        return FAL_PARAMETER_MAPPERS

    def _init_request(self, inputs: SegmentationInput) -> dict[str, Any]:
        """Build fal request from image and optional text prompt."""
        request: dict[str, Any] = {"image_url": build_data_url(inputs.image)}
        if inputs.prompt is not None:
            request["prompt"] = inputs.prompt
        return request

    def _parse_content(
        self,
        response_data: dict[str, Any],
    ) -> SegmentationContent:
        """Parse RLE masks, scores, and boxes from fal response."""
        result = super()._parse_content(response_data)
        rle = result.get("rle")
        if rle is None:
            msg = "No rle in response"
            raise ValueError(msg)

        rles = [rle] if isinstance(rle, str) else list(rle)
        scores = result.get("scores") or []
        boxes = result.get("boxes") or []
        metadata = result.get("metadata") or []

        masks: SegmentationContent = []
        for index, encoding in enumerate(rles):
            score = scores[index] if index < len(scores) else None
            box = boxes[index] if index < len(boxes) else None
            meta = metadata[index] if index < len(metadata) else None
            if isinstance(meta, dict):
                if score is None:
                    score = meta.get("score")
                if box is None:
                    box = meta.get("box")
                meta_index = meta.get("index", index)
            else:
                meta_index = index
            masks.append(
                SegmentationMask(
                    rle=encoding,
                    index=meta_index,
                    score=score,
                    box=box,
                )
            )
        return masks


__all__ = ["FalSegmentationClient"]
