"""Package registry for lazy loading entry points."""

import importlib.metadata

_loaded_packages: set[str] = set()
_loaded_providers: set[str] = set()


def _load_from_entry_points() -> None:
    """Load models and clients from installed packages via entry points."""

    entry_points = importlib.metadata.entry_points(group="celeste.packages")

    # Early return if all packages are already loaded
    entry_point_names = {ep.name for ep in entry_points}
    if entry_point_names.issubset(_loaded_packages):
        return

    for ep in entry_points:
        if ep.name in _loaded_packages:
            continue
        register_func = ep.load()
        # The function should register models and clients when called
        register_func()
        _loaded_packages.add(ep.name)


def _load_providers_from_entry_points() -> None:
    """Load auth from installed provider packages via entry points."""

    entry_points = importlib.metadata.entry_points(group="celeste.providers")

    # Early return if all providers are already loaded
    entry_point_names = {ep.name for ep in entry_points}
    if entry_point_names.issubset(_loaded_providers):
        return

    for ep in entry_points:
        if ep.name in _loaded_providers:
            continue
        register_func = ep.load()
        # The function should register auth types when called
        register_func()
        _loaded_providers.add(ep.name)
