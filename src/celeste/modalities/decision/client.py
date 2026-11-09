"""Decision modality client."""

from typing import Any, ClassVar, Unpack

from asgiref.sync import async_to_sync

from celeste.client import ModalityClient
from celeste.core import Modality
from celeste.types import DecisionContent, DecisionValue

from .io import (
    BooleanQuestion,
    BoxQuestion,
    ChoiceQuestion,
    DecisionChunk,
    DecisionFinishReason,
    DecisionInput,
    DecisionOutput,
    DecisionUsage,
    ScoreQuestion,
)
from .parameters import DecisionParameters


class DecisionClient(
    ModalityClient[
        DecisionInput,
        DecisionOutput,
        DecisionParameters,
        DecisionContent,
        DecisionChunk,
    ]
):
    """Base decision client with decide operation."""

    modality: Modality = Modality.DECISION
    _usage_class = DecisionUsage
    _finish_reason_class = DecisionFinishReason

    _decide_endpoint: ClassVar[str | None] = None

    @classmethod
    def _output_class(cls) -> type[DecisionOutput]:
        """Return the Output class for decision modality."""
        return DecisionOutput

    async def decide(
        self,
        state: DecisionValue,
        *,
        questions: dict[
            str, BooleanQuestion | ChoiceQuestion | ScoreQuestion | BoxQuestion
        ],
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[DecisionParameters],
    ) -> DecisionOutput:
        """Answer typed questions about a state."""
        inputs = DecisionInput(state=state, questions=questions)
        return await self._predict(
            inputs,
            endpoint=self._decide_endpoint,
            extra_body=extra_body,
            extra_headers=extra_headers,
            **parameters,
        )

    @property
    def sync(self) -> "DecisionSyncNamespace":
        """Sync namespace for decision operations."""
        return DecisionSyncNamespace(self)


class DecisionSyncNamespace:
    """Sync namespace for decision operations.

    Provides `client.sync.decide()`.
    """

    def __init__(self, client: DecisionClient) -> None:
        self._client = client

    def decide(
        self,
        state: DecisionValue,
        *,
        questions: dict[
            str, BooleanQuestion | ChoiceQuestion | ScoreQuestion | BoxQuestion
        ],
        extra_body: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
        **parameters: Unpack[DecisionParameters],
    ) -> DecisionOutput:
        """Blocking decision.

        Usage:
            result = client.sync.decide(state, questions=questions)
            print(result.content)
        """
        inputs = DecisionInput(state=state, questions=questions)
        return async_to_sync(self._client._predict)(
            inputs,
            endpoint=self._client._decide_endpoint,
            extra_body=extra_body,
            extra_headers=extra_headers,
            **parameters,
        )


__all__ = [
    "DecisionClient",
    "DecisionSyncNamespace",
]
