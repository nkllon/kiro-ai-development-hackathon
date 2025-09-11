#!/usr/bin/env python3
"""
Project Models - Project-related data classes

Extracted from models.py for RM-DDD compliance.
Single responsibility: Project-related data classes and models.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any

from .core_models import (
    SubmissionStatus, MediaType, TeamMember, ProjectLink, 
    MediaFile, SubmissionRequirement, SyncOperation, 
    FileChangeEvent, Deadline, DevpostConfig
)


@dataclass
class DevpostProject:
    """Complete Devpost project information."""
    project_id: str
    title: str
    description: str
    technologies: List[str] = field(default_factory=list)
    team_members: List[TeamMember] = field(default_factory=list)
    links: List[ProjectLink] = field(default_factory=list)
    media_files: List[MediaFile] = field(default_factory=list)
    submission_status: SubmissionStatus = SubmissionStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    hackathon_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectMetadata:
    """Local project metadata extracted from files."""
    project_id: str
    title: str
    description: str
    technologies: List[str] = field(default_factory=list)
    team_members: List[TeamMember] = field(default_factory=list)
    links: List[ProjectLink] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    project_path: str = ""
    last_modified: datetime = field(default_factory=datetime.now)
    file_count: int = 0
    total_size: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectSummary:
    """Summary information for multi-project management."""
    project_id: str
    title: str
    status: str
    last_activity: datetime
    team_size: int = 0
    file_count: int = 0
    completion_percentage: float = 0.0
    deadline_status: str = "unknown"
    sync_status: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyncResult:
    """Result of a synchronization operation."""
    success: bool
    operation_id: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    files_processed: int = 0
    files_failed: int = 0
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of validation operation."""
    is_valid: bool
    score: float
    issues_count: int
    critical_issues: int = 0
    warnings: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class PreviewData:
    """Data for preview generation."""
    project_id: str
    title: str
    description: str
    technologies: List[str] = field(default_factory=list)
    team_members: List[TeamMember] = field(default_factory=list)
    links: List[ProjectLink] = field(default_factory=list)
    media_files: List[MediaFile] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)
    preview_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectStatus:
    """Current project status information."""
    project_id: str
    is_active: bool
    last_sync: Optional[datetime] = None
    sync_status: str = "unknown"
    validation_status: str = "unknown"
    completion_status: str = "unknown"
    file_count: int = 0
    last_activity: datetime = field(default_factory=datetime.now)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthResult:
    """Authentication result."""
    success: bool
    user_id: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConnectionResult:
    """Project connection result."""
    success: bool
    project_id: str
    devpost_project_id: Optional[str] = None
    connection_url: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FormattingIssue:
    """Preview formatting issue."""
    issue_type: str
    severity: str
    message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompletionDetails:
    """Project completion status details."""
    project_id: str
    completion_percentage: float
    completed_requirements: List[str] = field(default_factory=list)
    pending_requirements: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    estimated_completion: Optional[datetime] = None
    blockers: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
