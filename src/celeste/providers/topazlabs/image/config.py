"""Configuration for Topaz Labs Image API."""

from enum import StrEnum


class TopazLabsImageEndpoint(StrEnum):
    """Endpoints for Topaz Labs Image API."""

    ENHANCE_ASYNC = "/enhance/async"
    ENHANCE_GEN_ASYNC = "/enhance-gen/async"
    TOOL_ASYNC = "/tool/async"
    STATUS = "/status/{process_id}"
    DOWNLOAD = "/download/{process_id}"


# Model id → submit endpoint for Gigapixel Image API intents.
# OpenAPI model enums omit some ids that model pages document (HF V3 on
# enhance, Detail on enhance-gen); catalog follows model pages. Live serving
# hard-rejects Faces on restore-gen despite model pages, so it is omitted.
SUBMIT_ENDPOINT_BY_MODEL: dict[str, str] = {
    "Standard V2": TopazLabsImageEndpoint.ENHANCE_ASYNC,
    "High Fidelity V2": TopazLabsImageEndpoint.ENHANCE_ASYNC,
    "Upscale High Fidelity V3": TopazLabsImageEndpoint.ENHANCE_ASYNC,
    "Low Resolution V2": TopazLabsImageEndpoint.ENHANCE_ASYNC,
    "CGI": TopazLabsImageEndpoint.ENHANCE_ASYNC,
    "Text Refine": TopazLabsImageEndpoint.ENHANCE_ASYNC,
    "Detail": TopazLabsImageEndpoint.ENHANCE_GEN_ASYNC,
    "Transparency Upscale": TopazLabsImageEndpoint.TOOL_ASYNC,
}


def submit_endpoint_for_model(model_id: str) -> str:
    """Resolve the async submit endpoint for a catalogued Topaz model id."""
    try:
        return SUBMIT_ENDPOINT_BY_MODEL[model_id]
    except KeyError:
        msg = f"No Topaz Image submit endpoint for model id: {model_id!r}"
        raise KeyError(msg) from None


BASE_URL = "https://api.topazlabs.com/image/v1"

POLLING_INTERVAL = 2.0
POLLING_TIMEOUT = 300.0
