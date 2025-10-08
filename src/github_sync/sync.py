"""
Synchronization engine for GitHub data.

This module provides the core synchronization logic for keeping local data
in sync with GitHub repositories, issues, pull requests, and commits.

This is a wrapper around the SynchronizationEngine from sync_engine.py to maintain
import compatibility.
"""

# Import the actual implementation from sync_engine
from .sync_engine import (
    SynchronizationEngine,
    SyncState,
    ChangeDetector,
    ConflictResolver
)

# Re-export for compatibility
__all__ = [
    'SynchronizationEngine',
    'SyncState', 
    'ChangeDetector',
    'ConflictResolver'
]