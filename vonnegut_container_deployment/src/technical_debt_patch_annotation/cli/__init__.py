"""
Technical Debt Patch Annotation CLI Package

This package provides command-line interfaces for managing technical debt patches,
including scanning, annotation creation, cleanup management, and batch operations.
"""

from .patch_cli import PatchCLI

__all__ = ['PatchCLI']