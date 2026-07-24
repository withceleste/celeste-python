"""Segmentation providers."""

from celeste.core import Provider

from ..client import SegmentationClient
from .fal import FalSegmentationClient

PROVIDERS: dict[Provider, type[SegmentationClient]] = {
    Provider.FAL: FalSegmentationClient,
}
