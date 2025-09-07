#!/usr/bin/env python3
"""
Devpost Integration Data Models

The Requirements ARE the Solution - Comprehensive Data Models
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator


# Enums for type safety and validation
class SubmissionStatus(str, Enum):
    """Devpost submission status enumeration."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    JUDGING = "judging"
    COMPLETE = "complete"
    WITHDRAWN = "withdrawn"


class ChangeType(str, Enum):
    """File change type enumeration."""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


class ContentType(str, Enum):
    """Content type enumeration for change detection."""
    DOCUMENTATION = "documentation"
    MEDIA = "media"
    SOURCE_CODE = "source_code"
    RELEASE = "release"
    CONFIGURATION = "configuration"


class SyncOperationType(str, Enum):
    """Sync operation type enumeration."""
    UPDATE_METADATA = "update_metadata"
    UPLOAD_MEDIA = "upload_media"
    UPDATE_DESCRIPTION = "update_description"
    UPDATE_TEAM = "update_team"
    UPDATE_LINKS = "update_links"
    UPDATE_TAGS = "update_tags"


class DeadlineType(str, Enum):
    """Hackathon deadline type enumeration."""
    SUBMISSION = "submission"
    JUDGING = "judging"
    FINAL = "final"
    MILESTONE = "milestone"


class MediaType(str, Enum):
    """Media file type enumeration."""
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    SCREENSHOT = "screenshot"
    DEMO = "demo"


class NotificationTiming(str, Enum):
    """Notification timing enumeration."""
    SEVEN_DAYS = "7_days"
    THREE_DAYS = "3_days"
    ONE_DAY = "1_day"
    SIX_HOURS = "6_hours"
    ONE_HOUR = "1_hour"
    THIRTY_MINUTES = "30_minutes"


class ConflictResolutionStrategy(str, Enum):
    """Multi-project conflict resolution strategy."""
    LOCAL_WINS = "local_wins"
    REMOTE_WINS = "remote_wins"
    MANUAL_RESOLUTION = "manual_resolution"
    TIMESTAMP_BASED = "timestamp_based"


class CompletionStatus(str, Enum):
    """Project completion status enumeration."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    READY_FOR_SUBMISSION = "ready_for_submission"
    SUBMITTED = "submitted"
    INCOMPLETE = "incomplete"


# Core Data Models
@dataclass
class TeamMember:
    """Team member information."""
    name: str
    email: Optional[str] = None
    role: Optional[str] = None
    devpost_username: Optional[str] = None


@dataclass
class ProjectLink:
    """Project link information."""
    title: str
    url: str
    link_type: str = "other"  # github, demo, video, etc.


@dataclass
class MediaFile:
    """Media file information."""
    filename: str
    file_path: Path
    media_type: MediaType
    caption: Optional[str] = None
    upload_url: Optional[str] = None
    file_size: Optional[int] = None
    uploaded_at: Optional[datetime] = None


@dataclass
class SubmissionRequirement:
    """Hackathon submission requirement."""
    requirement_id: str
    title: str
    description: str
    required: bool = True
    completed: bool = False
    validation_rule: Optional[str] = None


@dataclass
class DevpostProject:
    """Complete Devpost project information."""
    id: str
    title: str
    tagline: str
    description: str
    hackathon_id: str
    hackathon_name: str
    team_members: List[TeamMember] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    links: List[ProjectLink] = field(default_factory=list)
    media: List[MediaFile] = field(default_factory=list)
    submission_status: SubmissionStatus = SubmissionStatus.DRAFT
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    submission_requirements: List[SubmissionRequirement] = field(default_factory=list)
    completion_status: CompletionStatus = CompletionStatus.NOT_STARTED


@dataclass
class ProjectMetadata:
    """Local project metadata extracted from files."""
    title: str
    tagline: str
    description: str
    tags: List[str] = field(default_factory=list)
    team_members: List[str] = field(default_factory=list)
    repository_url: Optional[str] = None
    demo_url: Optional[str] = None
    video_url: Optional[str] = None
    version: Optional[str] = None
    changelog: Optional[str] = None


@dataclass
class SyncOperation:
    """Synchronization operation details."""
    operation_type: SyncOperationType
    target_field: str
    local_value: Any
    remote_value: Any
    priority: int = 1
    timestamp: datetime = field(default_factory=datetime.now)
    project_id: str = ""  # For multi-project isolation


@dataclass
class FileChangeEvent:
    """File system change event."""
    file_path: Path
    change_type: ChangeType
    timestamp: datetime = field(default_factory=datetime.now)
    affects_sync: bool = True
    content_type: ContentType = ContentType.SOURCE_CODE


# Deadline and Notification Models (Task 2.3)
@dataclass
class Deadline:
    """Hackathon deadline information."""
    hackathon_id: str
    project_id: str
    deadline_type: DeadlineType
    deadline_time: datetime
    requirements: List[SubmissionRequirement] = field(default_factory=list)
    notification_schedule: List[NotificationTiming] = field(default_factory=list)
    description: Optional[str] = None
    is_hard_deadline: bool = True
    
    def time_remaining(self) -> timedelta:
        """Calculate time remaining until deadline."""
        return self.deadline_time - datetime.now()
    
    def is_approaching(self, threshold: timedelta = timedelta(days=1)) -> bool:
        """Check if deadline is approaching within threshold."""
        return self.time_remaining() <= threshold
    
    def is_overdue(self) -> bool:
        """Check if deadline has passed."""
        return self.deadline_time < datetime.now()


@dataclass
class ProjectSummary:
    """Summary information for multi-project management."""
    project_id: str
    title: str
    hackathon_name: str
    deadline: Optional[datetime] = None
    submission_status: SubmissionStatus = SubmissionStatus.DRAFT
    completion_percentage: float = 0.0
    last_sync: Optional[datetime] = None
    pending_changes: int = 0
    validation_errors: int = 0
    is_active: bool = False


@dataclass
class NotificationSettings:
    """User notification preferences."""
    desktop_notifications: bool = True
    email_notifications: bool = False
    deadline_advance_times: List[timedelta] = field(
        default_factory=lambda: [
            timedelta(days=7),
            timedelta(days=1),
            timedelta(hours=1)
        ]
    )
    sync_failure_notifications: bool = True
    submission_status_notifications: bool = True
    quiet_hours_start: Optional[int] = None  # Hour of day (0-23)
    quiet_hours_end: Optional[int] = None    # Hour of day (0-23)


@dataclass
class ValidationRules:
    """Configurable validation rules for different hackathons."""
    required_fields: List[str] = field(
        default_factory=lambda: ["title", "tagline", "description"]
    )
    min_description_length: int = 100
    required_media_types: List[MediaType] = field(default_factory=list)
    team_member_validation: bool = True
    link_validation: bool = True
    max_tags: int = 10
    custom_rules: Dict[str, Any] = field(default_factory=dict)


# Configuration Models
@dataclass
class DevpostConfig:
    """Devpost integration configuration."""
    project_id: str
    hackathon_id: str
    auth_token: Optional[str] = None
    sync_enabled: bool = True
    watch_patterns: List[str] = field(
        default_factory=lambda: ["*.md", "*.py", "*.js", "*.json", "*.yml", "*.yaml"]
    )
    sync_interval: int = 300  # seconds
    auto_sync_media: bool = True
    notification_preferences: NotificationSettings = field(default_factory=NotificationSettings)
    deadline_reminders: List[NotificationTiming] = field(
        default_factory=lambda: [
            NotificationTiming.SEVEN_DAYS,
            NotificationTiming.ONE_DAY,
            NotificationTiming.ONE_HOUR
        ]
    )
    validation_rules: ValidationRules = field(default_factory=ValidationRules)


@dataclass
class ProjectConnection:
    """Local project to Devpost connection mapping."""
    local_path: Path
    devpost_project_id: str
    hackathon_id: str
    last_sync: Optional[datetime] = None
    sync_status: str = "never_synced"
    configuration: DevpostConfig = field(default_factory=lambda: DevpostConfig("", ""))
    is_active: bool = False  # For multi-project context switching


@dataclass
class MultiProjectConfig:
    """Multi-project management configuration."""
    active_project_id: Optional[str] = None
    project_connections: Dict[str, ProjectConnection] = field(default_factory=dict)
    global_settings: Dict[str, Any] = field(default_factory=dict)
    conflict_resolution_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.MANUAL_RESOLUTION


# Result and Status Models
@dataclass
class SyncResult:
    """Result of a synchronization operation."""
    success: bool
    changes_made: List[str] = field(default_factory=list)
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    sync_duration: Optional[timedelta] = None


@dataclass
class ValidationResult:
    """Result of validation operation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    missing_fields: List[str] = field(default_factory=list)
    completion_percentage: float = 0.0


@dataclass
class PreviewData:
    """Data for preview generation."""
    project_metadata: ProjectMetadata
    validation_result: ValidationResult
    media_files: List[MediaFile] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)
    template_version: str = "1.0"


@dataclass
class ProjectStatus:
    """Current project status information."""
    connected: bool = False
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    local_path: Optional[Path] = None
    last_sync: Optional[datetime] = None
    pending_changes: List[str] = field(default_factory=list)
    validation_errors: List[str] = field(default_factory=list)
    deadline: Optional[datetime] = None
    completion_status: CompletionStatus = CompletionStatus.NOT_STARTED


@dataclass
class AuthResult:
    """Authentication result."""
    success: bool
    token: Optional[str] = None
    expires_at: Optional[datetime] = None
    error: Optional[str] = None
    user_info: Optional[Dict[str, Any]] = None


@dataclass
class ConnectionResult:
    """Project connection result."""
    success: bool
    project: Optional[DevpostProject] = None
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


@dataclass
class ContextSwitchResult:
    """Multi-project context switch result."""
    success: bool
    previous_project_id: Optional[str] = None
    new_project_id: Optional[str] = None
    error: Optional[str] = None


@dataclass
class ConflictResolution:
    """Multi-project conflict resolution result."""
    conflicts_found: List[str] = field(default_factory=list)
    resolution_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.MANUAL_RESOLUTION
    resolved_conflicts: List[str] = field(default_factory=list)
    manual_intervention_required: bool = False


@dataclass
class ProjectDashboard:
    """Multi-project dashboard data."""
    projects: List[ProjectSummary] = field(default_factory=list)
    active_project: Optional[ProjectSummary] = None
    total_projects: int = 0
    projects_with_deadlines: int = 0
    overdue_projects: int = 0
    generated_at: datetime = field(default_factory=datetime.now)


# Notification Models
@dataclass
class NotificationMessage:
    """Notification message data."""
    title: str
    message: str
    project_id: str
    notification_type: str = "info"  # info, warning, error, deadline
    action_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    delivered: bool = False


@dataclass
class ReminderTiming:
    """Deadline reminder timing configuration."""
    advance_time: timedelta
    notification_type: str = "deadline_reminder"
    enabled: bool = True
    custom_message: Optional[str] = None


@dataclass
class GlobalSettings:
    """Global settings for multi-project management."""
    default_sync_interval: int = 300
    max_concurrent_projects: int = 10
    auto_switch_on_file_change: bool = False
    unified_notifications: bool = True
    backup_configurations: bool = True
    analytics_enabled: bool = True


# Error and Exception Models
@dataclass
class FormattingIssue:
    """Preview formatting issue."""
    field_name: str
    issue_type: str
    description: str
    severity: str = "warning"  # info, warning, error
    suggested_fix: Optional[str] = None


@dataclass
class CompletionStatus:
    """Project completion status details."""
    overall_percentage: float = 0.0
    required_fields_complete: bool = False
    media_uploaded: bool = False
    team_configured: bool = False
    links_added: bool = False
    description_adequate: bool = False
    ready_for_submission: bool = False
    last_updated: datetime = field(default_factory=datetime.now)


# Utility functions for model validation and conversion
def validate_project_metadata(metadata: ProjectMetadata) -> ValidationResult:
    """Validate project metadata against requirements."""
    errors = []
    warnings = []
    missing_fields = []
    
    # Required field validation
    if not metadata.title or len(metadata.title.strip()) < 3:
        errors.append("Title must be at least 3 characters long")
        missing_fields.append("title")
    
    if not metadata.tagline or len(metadata.tagline.strip()) < 10:
        errors.append("Tagline must be at least 10 characters long")
        missing_fields.append("tagline")
    
    if not metadata.description or len(metadata.description.strip()) < 100:
        errors.append("Description must be at least 100 characters long")
        missing_fields.append("description")
    
    # Warning validations
    if len(metadata.tags) == 0:
        warnings.append("No tags specified - consider adding relevant tags")
    
    if len(metadata.team_members) == 0:
        warnings.append("No team members specified")
    
    # Calculate completion percentage
    total_checks = 5  # title, tagline, description, tags, team_members
    passed_checks = 0
    
    if metadata.title and len(metadata.title.strip()) >= 3:
        passed_checks += 1
    if metadata.tagline and len(metadata.tagline.strip()) >= 10:
        passed_checks += 1
    if metadata.description and len(metadata.description.strip()) >= 100:
        passed_checks += 1
    if len(metadata.tags) > 0:
        passed_checks += 1
    if len(metadata.team_members) > 0:
        passed_checks += 1
    
    completion_percentage = (passed_checks / total_checks) * 100
    
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        missing_fields=missing_fields,
        completion_percentage=completion_percentage
    )


def create_default_notification_settings() -> NotificationSettings:
    """Create default notification settings."""
    return NotificationSettings(
        desktop_notifications=True,
        email_notifications=False,
        deadline_advance_times=[
            timedelta(days=7),
            timedelta(days=3),
            timedelta(days=1),
            timedelta(hours=6),
            timedelta(hours=1)
        ],
        sync_failure_notifications=True,
        submission_status_notifications=True
    )


def create_default_validation_rules() -> ValidationRules:
    """Create default validation rules."""
    return ValidationRules(
        required_fields=["title", "tagline", "description"],
        min_description_length=100,
        required_media_types=[],
        team_member_validation=True,
        link_validation=True,
        max_tags=10
    )


# Export all models for easy importing
__all__ = [
    # Enums
    "SubmissionStatus", "ChangeType", "ContentType", "SyncOperationType",
    "DeadlineType", "MediaType", "NotificationTiming", "ConflictResolutionStrategy",
    "CompletionStatus",
    
    # Core Models
    "TeamMember", "ProjectLink", "MediaFile", "SubmissionRequirement",
    "DevpostProject", "ProjectMetadata", "SyncOperation", "FileChangeEvent",
    
    # Deadline and Notification Models (Task 2.3)
    "Deadline", "ProjectSummary", "NotificationSettings", "ValidationRules",
    "NotificationMessage", "ReminderTiming", "GlobalSettings",
    
    # Configuration Models
    "DevpostConfig", "ProjectConnection", "MultiProjectConfig",
    
    # Result and Status Models
    "SyncResult", "ValidationResult", "PreviewData", "ProjectStatus",
    "AuthResult", "ConnectionResult", "ContextSwitchResult", "ConflictResolution",
    "ProjectDashboard", "FormattingIssue", "CompletionStatus",
    
    # Utility Functions
    "validate_project_metadata", "create_default_notification_settings",
    "create_default_validation_rules"
]