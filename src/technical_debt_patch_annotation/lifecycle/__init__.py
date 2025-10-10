"""
Patch Lifecycle Management Module.

This module provides comprehensive lifecycle management for technical debt patches,
including creation tracking, expiration monitoring, automated notifications, and
escalation workflows.
"""

from .manager import PatchLifecycleManager

__all__ = ['PatchLifecycleManager']