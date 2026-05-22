from celeste.core import InputType
from celeste.mime_types import ImageMimeType
from celeste.tools import ToolError, ToolOutput


def test_tool_output_wraps_structured_content_and_metadata() -> None:
    output = ToolOutput[list[dict[str, str | None]]](
        content=[
            {
                "id": "image-1",
                "artifact_type": InputType.IMAGE,
                "mime_type": ImageMimeType.PNG,
            }
        ],
        metadata={"provider": "test"},
    )

    assert output.model_dump(mode="json") == {
        "content": [
            {
                "id": "image-1",
                "artifact_type": "image",
                "mime_type": "image/png",
            }
        ],
        "metadata": {"provider": "test"},
    }


def test_tool_output_metadata_defaults_to_empty_dict() -> None:
    output = ToolOutput[dict[str, bool]](content={"ok": True})

    assert output.metadata == {}


def test_tool_error_wraps_error_content_code_and_metadata() -> None:
    error = ToolError[str](
        content="quota exceeded",
        code="provider_call_failed",
        metadata={"retryable": False},
    )

    assert error.model_dump(mode="json") == {
        "content": "quota exceeded",
        "code": "provider_call_failed",
        "metadata": {"retryable": False},
    }
