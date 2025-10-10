"""Compatibility layer for repository discovery core modules.

The concrete implementations live in :mod:`repo_discovery_core`. These
shims are kept to avoid breaking existing imports inside the codebase.
"""

from repo_discovery_core import (
    ContentClassifier,
    ContentInventoryManager,
    ContentMetadataExtractor,
    ContentScanner,
)

__all__ = [
    "ContentClassifier",
    "ContentInventoryManager",
    "ContentMetadataExtractor",
    "ContentScanner",
]

