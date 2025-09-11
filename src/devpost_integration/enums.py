#!/usr/bin/env python3
"""
Enums - Core enumeration definitions

Extracted from core_models.py for RM-DDD compliance.
Single responsibility: Core enumeration definitions.
"""

from enum import Enum


class SubmissionStatus(str, Enum):
    """Devpost submission status enumeration."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    WINNER = "winner"


class ChangeType(str, Enum):
    """File change type enumeration."""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"
    RENAMED = "renamed"


class ContentType(str, Enum):
    """Content type enumeration for change detection."""
    CODE = "code"
    DOCUMENTATION = "documentation"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    CONFIG = "config"
    OTHER = "other"


class SyncOperationType(str, Enum):
    """Sync operation type enumeration."""
    UPLOAD = "upload"
    DOWNLOAD = "download"
    UPDATE = "update"
    DELETE = "delete"
    SYNC = "sync"
    VALIDATE = "validate"


class DeadlineType(str, Enum):
    """Hackathon deadline type enumeration."""
    SUBMISSION = "submission"
    REGISTRATION = "registration"
    JUDGING = "judging"
    ANNOUNCEMENT = "announcement"
    CUSTOM = "custom"


class MediaType(str, Enum):
    """Media file type enumeration."""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    OTHER = "other"


class NotificationTiming(str, Enum):
    """Notification timing enumeration."""
    IMMEDIATE = "immediate"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"


class ConflictResolutionStrategy(str, Enum):
    """Multi-project conflict resolution strategy."""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    PROMPT = "prompt"
    IGNORE = "ignore"


class CompletionStatus(str, Enum):
    """Project completion status enumeration."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class ValidationSeverity(str, Enum):
    """Validation issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"
