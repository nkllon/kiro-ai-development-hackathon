#!/usr/bin/env python3
"""
Models - Unified model imports for Devpost Integration

Refactored for RM-DDD compliance by importing from decomposed modules.
Single responsibility: Model imports and re-exports.
"""

# Import all models from decomposed modules
from .core_models import *
from .project_models import *
from .multi_project_models import *

# Re-export everything for backward compatibility
__all__ = [
    # Core enums
    'SubmissionStatus', 'ChangeType', 'ContentType', 'SyncOperationType',
    'DeadlineType', 'MediaType', 'NotificationTiming', 'ConflictResolutionStrategy',
    'CompletionStatus', 'ValidationSeverity',
    
    # Core data classes
    'TeamMember', 'ProjectLink', 'MediaFile', 'SubmissionRequirement',
    'SyncOperation', 'FileChangeEvent', 'Deadline', 'NotificationSettings',
    'ValidationRules', 'DevpostConfig',
    
    # Project data classes
    'DevpostProject', 'ProjectMetadata', 'ProjectSummary', 'SyncResult',
    'ValidationResult', 'PreviewData', 'ProjectStatus', 'AuthResult',
    'ConnectionResult', 'FormattingIssue', 'CompletionDetails',
    
    # Multi-project data classes
    'ProjectConnection', 'MultiProjectConfig', 'ContextSwitchResult',
    'ConflictResolution', 'ProjectDashboard', 'NotificationMessage',
    'ReminderTiming', 'GlobalSettings'
]