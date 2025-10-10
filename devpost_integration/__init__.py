"""Compatibility shim that exposes the DevPost integration package at the
repository root.

Historically tooling imported ``devpost_integration`` directly, but the current
code lives under ``src.devpost_integration``.  Importing this package now
transparently proxies to the canonical implementation while preserving the
expected module layout for third-party consumers.
"""

from __future__ import annotations

import importlib
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import List

_SRC_PACKAGE = "src.devpost_integration"

_src_module: ModuleType = importlib.import_module(_SRC_PACKAGE)

__all__ = getattr(_src_module, "__all__", [])
__path__ = list(getattr(_src_module, "__path__", []))

_spec = ModuleSpec(name=__name__, loader=None, is_package=True)
_spec.submodule_search_locations = list(__path__)
__spec__ = _spec

def __getattr__(name: str):  # pragma: no cover - thin proxy
    return getattr(_src_module, name)


def __dir__() -> List[str]:  # pragma: no cover - thin proxy
    return sorted(set(globals()) | set(dir(_src_module)))

