#!/usr/bin/env python3
"""
Multi-Project Manager - Unified multi-project management

Refactored for RM-DDD compliance by importing from decomposed modules.
Single responsibility: Multi-project management imports and re-exports.
"""

from .multi_project_config import MultiProjectConfig
from .project_context_manager import ProjectContextManager
from .conflict_resolution import ConflictResolver
from .multi_project_orchestrator import MultiProjectOrchestrator

# Re-export everything for backward compatibility
__all__ = [
    'MultiProjectConfig',
    'ProjectContextManager', 
    'ConflictResolver',
    'MultiProjectOrchestrator'
]
