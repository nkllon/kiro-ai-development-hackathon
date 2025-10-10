"""Top-level package for the DevPost integration.

This module restores the original package semantics that other tools in the
repository expect.  It exposes the most frequently used entry points from the
individual DevPost integration modules while deferring to those modules for the
full implementation details.
"""

from __future__ import annotations

from importlib import import_module
from typing import Dict, List

__all__: List[str] = []

# Mapping of public symbols that should be importable directly from the package
# to the module that defines them.  Not every legacy symbol is present in the
# trimmed down DevPost integration code base, so we lazily resolve each symbol
# and only expose the ones that actually exist today.
_SYMBOL_MAP: Dict[str, str] = {
    # Core services
    "DevPostAPIClient": "api_client.DevPostAPIClient",
    "ApiClient": "api_client.ApiClient",
    "DevPostAuthService": "auth_service.DevPostAuthService",
    "AuthService": "auth_service.AuthService",
    # Project management helpers
    "DevpostProjectManager": "project_manager.DevpostProjectManager",
    "ProjectStatus": "project_manager.ProjectStatus",
    # Synchronisation layer
    "DevpostSyncManager": "sync_manager.DevpostSyncManager",
    "SyncStatus": "sync_manager.SyncStatus",
    "SyncPriority": "sync_manager.SyncPriority",
    "QueuedSyncOperation": "sync_manager.QueuedSyncOperation",
    # Preview tooling
    "DevpostPreviewGenerator": "preview_generator.DevpostPreviewGenerator",
    "RealtimePreviewManager": "preview_generator.RealtimePreviewManager",
    # Reflective module utilities
    "ReflectiveModule": "reflective_module.ReflectiveModule",
    "ReflectiveModuleRegistry": "module_registry.ReflectiveModuleRegistry",
    "ModuleHealth": "reflective_module.ModuleHealth",
    "ModuleStatus": "reflective_module.ModuleStatus",
    "ModuleCapability": "reflective_module.ModuleCapability",
    "GracefulDegradationResult": "reflective_module.GracefulDegradationResult",
    "register_module": "reflective_module.register_module",
}

# Symbols that we could not eagerly resolve are tracked so that __getattr__ can
# attempt to load them lazily when requested.
_lazy_symbols: Dict[str, str] = {}


def _export(symbols: Dict[str, str]) -> None:
    """Try to load and expose the given symbols immediately."""

    for public_name, target in list(symbols.items()):
        module_name, attribute = target.rsplit(".", 1)
        try:
            module = import_module(f"{__name__}.{module_name}")
            value = getattr(module, attribute)
        except (ModuleNotFoundError, AttributeError, ImportError):
            # Defer the lookup so that consumers still get a helpful error if
            # they request a symbol that is no longer implemented.
            _lazy_symbols[public_name] = target
            continue

        globals()[public_name] = value
        __all__.append(public_name)
        # Remove successfully exported symbols so that __getattr__ knows it
        # doesn't need to handle them.
        symbols.pop(public_name, None)


_export(dict(_SYMBOL_MAP))


def __getattr__(name: str):  # pragma: no cover - convenience bridge
    """Provide lazy access to symbols that were not available eagerly."""

    target = _lazy_symbols.get(name)
    if not target:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    module_name, attribute = target.rsplit(".", 1)
    try:
        module = import_module(f"{__name__}.{module_name}")
        value = getattr(module, attribute)
    except (ImportError, AttributeError) as exc:  # pragma: no cover - defensive guard
        raise AttributeError(
            f"module '{__name__}' has no attribute '{name}'"
        ) from exc

    globals()[name] = value
    __all__.append(name)
    _lazy_symbols.pop(name, None)
    return value


def __dir__() -> List[str]:  # pragma: no cover - user convenience
    return sorted(set(__all__) | set(_SYMBOL_MAP) | set(globals()))

