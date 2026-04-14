"""Tests for the ambient authentication context primitive."""

import asyncio
import contextvars
from concurrent.futures import ThreadPoolExecutor

import pytest
from pydantic import SecretStr, ValidationError

from celeste.auth import AuthHeader, NoAuth
from celeste.authentication_context import (
    AuthenticationContext,
    _current_context,
    authentication_scope,
    resolve_authentication,
)
from celeste.core import Modality, Operation
from celeste.exceptions import MissingAuthenticationError


@pytest.fixture
def text_auth() -> AuthHeader:
    return AuthHeader(secret=SecretStr("text-key"))


@pytest.fixture
def images_auth() -> AuthHeader:
    return AuthHeader(secret=SecretStr("images-key"))


@pytest.fixture
def audio_auth() -> NoAuth:
    return NoAuth()


@pytest.fixture
def full_context(
    text_auth: AuthHeader,
    images_auth: AuthHeader,
    audio_auth: NoAuth,
) -> AuthenticationContext:
    return AuthenticationContext(
        entries={
            (Modality.TEXT, Operation.GENERATE): text_auth,
            (Modality.IMAGES, Operation.GENERATE): images_auth,
            (Modality.AUDIO, Operation.SPEAK): audio_auth,
        }
    )


class TestAuthenticationContextModel:
    def test_frozen_rejects_mutation(self, full_context: AuthenticationContext) -> None:
        with pytest.raises(ValidationError):
            full_context.entries = {}  # type: ignore[misc]

    def test_get_for_returns_bound_entry(
        self, full_context: AuthenticationContext, text_auth: AuthHeader
    ) -> None:
        assert full_context.get_for(Modality.TEXT, Operation.GENERATE) is text_auth

    def test_get_for_missing_entry_returns_none(
        self, full_context: AuthenticationContext
    ) -> None:
        assert full_context.get_for(Modality.VIDEOS, Operation.GENERATE) is None


class TestAuthenticationScope:
    def test_outside_scope_resolves_none(self) -> None:
        assert resolve_authentication(Modality.TEXT, Operation.GENERATE) is None

    def test_inside_scope_resolves_bound_auth(
        self, full_context: AuthenticationContext, text_auth: AuthHeader
    ) -> None:
        with authentication_scope(full_context):
            assert (
                resolve_authentication(Modality.TEXT, Operation.GENERATE) is text_auth
            )

    def test_exit_restores_previous_state(
        self, full_context: AuthenticationContext
    ) -> None:
        assert _current_context.get() is None
        with authentication_scope(full_context):
            assert _current_context.get() is full_context
        assert _current_context.get() is None

    def test_nested_scopes_inner_wins_outer_restored(
        self,
        full_context: AuthenticationContext,
        text_auth: AuthHeader,
    ) -> None:
        inner_auth = AuthHeader(secret=SecretStr("inner-key"))
        inner_context = AuthenticationContext(
            entries={(Modality.TEXT, Operation.GENERATE): inner_auth}
        )

        with authentication_scope(full_context):
            assert (
                resolve_authentication(Modality.TEXT, Operation.GENERATE) is text_auth
            )
            with authentication_scope(inner_context):
                assert (
                    resolve_authentication(Modality.TEXT, Operation.GENERATE)
                    is inner_auth
                )
            assert (
                resolve_authentication(Modality.TEXT, Operation.GENERATE) is text_auth
            )

    def test_scope_with_none_clears_binding(
        self, full_context: AuthenticationContext
    ) -> None:
        with authentication_scope(full_context):
            with authentication_scope(None):
                assert resolve_authentication(Modality.TEXT, Operation.GENERATE) is None
            assert _current_context.get() is full_context


class TestResolveAuthentication:
    def test_scope_bound_but_entry_missing_raises(
        self, full_context: AuthenticationContext
    ) -> None:
        with (
            authentication_scope(full_context),
            pytest.raises(MissingAuthenticationError) as exc_info,
        ):
            resolve_authentication(Modality.VIDEOS, Operation.GENERATE)
        err = exc_info.value
        assert err.modality is Modality.VIDEOS
        assert err.operation is Operation.GENERATE
        assert "videos/generate" in str(err)

    def test_scope_bound_with_explicit_none_raises(self) -> None:
        context = AuthenticationContext(
            entries={(Modality.TEXT, Operation.GENERATE): None}
        )
        with (
            authentication_scope(context),
            pytest.raises(MissingAuthenticationError),
        ):
            resolve_authentication(Modality.TEXT, Operation.GENERATE)


class TestAsyncPropagation:
    @pytest.mark.asyncio
    async def test_create_task_propagates(
        self, full_context: AuthenticationContext, images_auth: AuthHeader
    ) -> None:
        async def child() -> object:
            return resolve_authentication(Modality.IMAGES, Operation.GENERATE)

        with authentication_scope(full_context):
            task = asyncio.create_task(child())
            result = await task

        assert result is images_auth

    @pytest.mark.asyncio
    async def test_gather_siblings_share_snapshot(
        self, full_context: AuthenticationContext, images_auth: AuthHeader
    ) -> None:
        async def child() -> object:
            return resolve_authentication(Modality.IMAGES, Operation.GENERATE)

        with authentication_scope(full_context):
            results = await asyncio.gather(child(), child(), child())

        assert all(r is images_auth for r in results)

    @pytest.mark.asyncio
    async def test_to_thread_propagates(
        self, full_context: AuthenticationContext, text_auth: AuthHeader
    ) -> None:
        def sync_worker() -> object:
            return resolve_authentication(Modality.TEXT, Operation.GENERATE)

        with authentication_scope(full_context):
            result = await asyncio.to_thread(sync_worker)

        assert result is text_auth

    def test_raw_thread_pool_does_not_propagate(
        self, full_context: AuthenticationContext
    ) -> None:
        def sync_worker() -> object:
            return resolve_authentication(Modality.TEXT, Operation.GENERATE)

        with (
            ThreadPoolExecutor(max_workers=1) as pool,
            authentication_scope(full_context),
        ):
            future = pool.submit(sync_worker)
            result = future.result()

        assert result is None

    def test_raw_thread_pool_with_copy_context_propagates(
        self, full_context: AuthenticationContext, text_auth: AuthHeader
    ) -> None:
        def sync_worker() -> object:
            return resolve_authentication(Modality.TEXT, Operation.GENERATE)

        with (
            ThreadPoolExecutor(max_workers=1) as pool,
            authentication_scope(full_context),
        ):
            ctx_snapshot = contextvars.copy_context()
            future = pool.submit(ctx_snapshot.run, sync_worker)
            result = future.result()

        assert result is text_auth
