"""Google GenerateContent native grounding helpers."""

from typing import Any


def parse_grounding_metadata(response_data: dict[str, Any]) -> dict[str, Any] | None:
    """Extract Gemini groundingMetadata from the first candidate."""
    candidates = response_data.get("candidates", [])
    meta = candidates[0].get("groundingMetadata") if candidates else None
    return meta if isinstance(meta, dict) else None


def merge_grounding_metadata(metadata: list[dict[str, Any]]) -> dict[str, Any]:
    """Merge streamed Gemini grounding metadata chunks."""
    combined: dict[str, Any] = {
        "webSearchQueries": [],
        "groundingChunks": [],
        "groundingSupports": [],
    }
    for meta in metadata:
        for key in ("webSearchQueries", "groundingChunks", "groundingSupports"):
            combined[key].extend(meta.get(key, []))
        if meta.get("searchEntryPoint"):
            combined["searchEntryPoint"] = meta["searchEntryPoint"]
    return combined


__all__ = ["merge_grounding_metadata", "parse_grounding_metadata"]
