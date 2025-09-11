#!/usr/bin/env python3
"""
Core Models - Unified core model imports

Refactored for RM-DDD compliance by importing from decomposed modules.
Single responsibility: Core model imports and re-exports.
"""

# Import all core models from decomposed modules
from .enums import *
from .base_models import *

# Re-export everything for backward compatibility
__all__ = [
    # Enums
    'SubmissionStatus', 'ChangeType', 'ContentType', 'SyncOperationType',
    'DeadlineType', 'MediaType', 'NotificationTiming', 'ConflictResolutionStrategy',
    'CompletionStatus', 'ValidationSeverity',
    
    # Base data classes
    'TeamMember', 'ProjectLink', 'MediaFile', 'SubmissionRequirement',
    'SyncOperation', 'FileChangeEvent', 'Deadline', 'NotificationSettings',
    'ValidationRules', 'DevpostConfig'
]
