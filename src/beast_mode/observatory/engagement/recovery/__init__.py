"""
Recovery System for Live Dashboard Engagement System
====================================================

Provides recovery mechanisms for systematic execution failures,
including task method generation and graceful degradation.
"""

from .task_method_generator import TaskMethodGenerator

__all__ = ["TaskMethodGenerator"]