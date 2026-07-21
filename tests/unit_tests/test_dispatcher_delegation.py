"""Dispatcher delegation contract: every backend-customized hook must be forwarded."""

import inspect
import types
import typing
from collections.abc import Callable

import pytest

from celeste import _CLIENT_MAP
from celeste.client import ModalityClient

_HOOK_KINDS = (types.FunctionType, classmethod, staticmethod, property)
# Required only when a backend actually streams (defines _stream_class): the
# streaming namespaces call _stream_class first, which base-raises otherwise.
_STREAMING_HOOKS = frozenset({"_make_stream_request", "_stream_class"})
# Construction hook: pydantic injects per-class init_private_attributes wrappers
# that break identity comparison.
_EXCLUDED = frozenset({"model_post_init"})
# Hooks whose base implementation reads per-class state, so method identity
# alone cannot see divergence: hook name -> the state the base impl reads.
_STATE_DRIVEN_HOOKS: dict[str, Callable[[type[ModalityClient]], object]] = {
    "_build_metadata": lambda c: c._content_fields,
    "_transform_output": lambda c: list(c.parameter_mappers()),
}


def _dispatchers() -> list[type[ModalityClient]]:
    """Registered clients whose private-attr union selects backend clients."""
    found: dict[type[ModalityClient], None] = {}
    for cls in _CLIENT_MAP.values():
        for name in cls.__private_attributes__:
            hint = typing.get_type_hints(cls).get(name)
            backends = [
                arg
                for arg in typing.get_args(hint)
                if isinstance(arg, type) and issubclass(arg, ModalityClient)
            ]
            if backends:
                assert name == "_strategy", (
                    f"{cls.__name__}: dispatcher attr is {name!r} — rename to "
                    "_strategy or extend test_dispatcher_delegation.py"
                )
                found[cls] = None
    return list(found)


def _backends(dispatcher: type[ModalityClient]) -> list[type[ModalityClient]]:
    """Backend classes from the dispatcher's _strategy union annotation."""
    union = typing.get_type_hints(dispatcher)["_strategy"]
    return [arg for arg in typing.get_args(union) if arg is not type(None)]


def _hook_names(modality_base: type[ModalityClient]) -> set[str]:
    """Every celeste-defined callable name reachable on the modality base."""
    return {
        name
        for klass in modality_base.__mro__
        if klass.__module__.startswith("celeste")
        for name, attr in vars(klass).items()
        if not name.startswith("__")
        and isinstance(attr, _HOOK_KINDS)
        and name not in _EXCLUDED
    }


def test_registry_discovers_known_dispatchers() -> None:
    names = {d.__name__ for d in _dispatchers()}
    assert {"GoogleTextClient", "GoogleImagesClient", "GoogleVideosClient"} <= names


@pytest.mark.parametrize("dispatcher", _dispatchers(), ids=lambda d: d.__name__)
def test_dispatcher_defines_every_backend_customized_hook(
    dispatcher: type[ModalityClient],
) -> None:
    modality_base = next(
        c for c in dispatcher.__mro__[1:] if issubclass(c, ModalityClient)
    )
    assert modality_base is not ModalityClient
    backends = _backends(dispatcher)
    assert len(backends) >= 2, f"{dispatcher.__name__}: dispatcher needs >= 2 backends"
    assert all(issubclass(b, modality_base) for b in backends)
    hook_names = _hook_names(modality_base)
    assert len(hook_names) >= 20, "hook derivation broke — sweep would be hollow"

    streaming_served = any(
        inspect.getattr_static(backend, "_stream_class")
        is not inspect.getattr_static(modality_base, "_stream_class")
        for backend in backends
    )

    required: dict[str, str] = {}
    for name in hook_names:
        if name in _STREAMING_HOOKS and not streaming_served:
            continue
        customizing = [
            backend.__name__
            for backend in backends
            if inspect.getattr_static(backend, name)
            is not inspect.getattr_static(modality_base, name)
        ]
        if customizing:
            required[name] = f"customized by {', '.join(customizing)}"
    for name, state in _STATE_DRIVEN_HOOKS.items():
        diverging = [b.__name__ for b in backends if state(b) != state(dispatcher)]
        if diverging and name not in required:
            required[name] = (
                f"state the base impl reads differs in {', '.join(diverging)}"
            )

    missing = [
        f"{name} ({required[name]})"
        for name in sorted(required)
        if name not in vars(dispatcher)
    ]
    assert not missing, (
        f"{dispatcher.__name__} must define these hooks — without a delegate the "
        f"{modality_base.__name__} implementation runs silently: " + "; ".join(missing)
    )
