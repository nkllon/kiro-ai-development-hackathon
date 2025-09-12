"""
Enumeration Models for DevPost Integration

This module contains all enumeration types used throughout
the DevPost integration system.

RM-DDD Compliance:
- Each enum is properly documented
- Values are meaningful and consistent
- Under 300 lines per module
"""

from enum import Enum


class SyncOperationType(Enum):
    """Types of synchronization operations."""
    FULL_SYNC = "full_sync"
    INCREMENTAL_SYNC = "incremental_sync"
    METADATA_SYNC = "metadata_sync"
    FILE_SYNC = "file_sync"
    CONFIG_SYNC = "config_sync"


class ChangeType(Enum):
    """Types of file changes."""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"
    MOVED = "moved"


class MediaType(Enum):
    """Types of media files."""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    OTHER = "other"


class ConflictResolutionStrategy(Enum):
    """Strategies for resolving conflicts."""
    KEEP_LOCAL = "keep_local"
    KEEP_REMOTE = "keep_remote"
    MERGE = "merge"
    MANUAL = "manual"
    SKIP = "skip"


class SubmissionStatus(Enum):
    """Status of project submissions."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ContentType(Enum):
    """Types of content."""
    TEXT = "text"
    CODE = "code"
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    YAML = "yaml"
    XML = "xml"
    BINARY = "binary"


class DeadlineType(Enum):
    """Types of deadlines."""
    SUBMISSION = "submission"
    REVIEW = "review"
    JUDGING = "judging"
    ANNOUNCEMENT = "announcement"
    CUSTOM = "custom"


class NotificationTiming(Enum):
    """Timing for notifications."""
    IMMEDIATE = "immediate"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"
    NEVER = "never"
