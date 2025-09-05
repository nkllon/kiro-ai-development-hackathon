"""
Data models for Devpost integration.

This module defines all the data structures used throughout the Devpost
integration system, including projects, metadata, sync operations, and
configuration models.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict, HttpUrl
import re
import json


class SubmissionStatus(str, Enum):
    """Project submission status on Devpost."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PUBLISHED = "published"
    WITHDRAWN = "withdrawn"


class ChangeType(str, Enum):
    """File change types for monitoring."""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


class SyncOperationType(str, Enum):
    """Types of sync operations."""
    METADATA_UPDATE = "metadata_update"
    MEDIA_UPLOAD = "media_upload"
    DOCUMENTATION_UPDATE = "documentation_update"
    FULL_SYNC = "full_sync"


class SyncStatus(str, Enum):
    """Synchronization status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


@dataclass
class TeamMember:
    """Represents a team member in a hackathon project."""
    username: str
    display_name: str
    profile_url: Optional[str] = None
    avatar_url: Optional[str] = None


@dataclass
class ProjectLink:
    """Represents a project link (demo, repository, etc.)."""
    title: str
    url: str
    link_type: str  # "repository", "demo", "video", "other"


@dataclass
class MediaFile:
    """Represents a media file associated with the project."""
    filename: str
    url: str
    file_type: str  # "image", "video", "document"
    size_bytes: Optional[int] = None
    uploaded_at: Optional[datetime] = None


class DevpostProject(BaseModel):
    """Represents a Devpost hackathon project."""
    
    id: str = Field(..., description="Unique project identifier")
    title: str = Field(..., description="Project title")
    tagline: str = Field(..., description="Short project description")
    description: str = Field(..., description="Full project description")
    hackathon_id: str = Field(..., description="Associated hackathon ID")
    hackathon_name: str = Field(..., description="Hackathon display name")
    team_members: List[TeamMember] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    links: List[ProjectLink] = Field(default_factory=list)
    media: List[MediaFile] = Field(default_factory=list)
    submission_status: SubmissionStatus = Field(default=SubmissionStatus.DRAFT)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    
    @field_validator('title')
    @classmethod
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Project title cannot be empty')
        return v.strip()
    
    @field_validator('tagline')
    @classmethod
    def tagline_length_check(cls, v):
        if len(v) > 120:
            raise ValueError('Tagline must be 120 characters or less')
        return v
    
    @field_validator('description')
    @classmethod
    def description_length_check(cls, v):
        if len(v) > 5000:
            raise ValueError('Description must be 5000 characters or less')
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        for tag in v:
            if len(tag) > 50:
                raise ValueError('Each tag must be 50 characters or less')
            if not re.match(r'^[a-zA-Z0-9\-_\s]+$', tag):
                raise ValueError('Tags can only contain letters, numbers, hyphens, underscores, and spaces')
        return v
    
    @model_validator(mode='after')
    def validate_deadline(self):
        if self.deadline and self.deadline <= datetime.now():
            raise ValueError('Deadline must be in the future')
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API serialization."""
        return self.model_dump(mode='json', exclude_none=True)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DevpostProject':
        """Create instance from dictionary."""
        return cls.model_validate(data)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(exclude_none=True)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'DevpostProject':
        """Create instance from JSON string."""
        return cls.model_validate_json(json_str)


class ProjectMetadata(BaseModel):
    """Local project metadata extracted from files."""
    
    title: str = Field(..., description="Project title")
    tagline: str = Field(default="", description="Short description")
    description: str = Field(default="", description="Full description")
    tags: List[str] = Field(default_factory=list)
    team_members: List[str] = Field(default_factory=list)
    repository_url: Optional[str] = None
    demo_url: Optional[str] = None
    video_url: Optional[str] = None
    readme_path: Optional[Path] = None
    package_info: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Project title cannot be empty')
        if len(v) > 200:
            raise ValueError('Title must be 200 characters or less')
        return v.strip()
    
    @field_validator('tagline')
    @classmethod
    def validate_tagline(cls, v):
        if len(v) > 120:
            raise ValueError('Tagline must be 120 characters or less')
        return v
    
    @field_validator('repository_url', 'demo_url', 'video_url')
    @classmethod
    def validate_urls(cls, v):
        if v and not re.match(r'^https?://', v):
            raise ValueError('URLs must start with http:// or https://')
        return v
    
    @field_validator('team_members')
    @classmethod
    def validate_team_members(cls, v):
        if len(v) > 20:
            raise ValueError('Maximum 20 team members allowed')
        for member in v:
            if len(member) > 100:
                raise ValueError('Team member name must be 100 characters or less')
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.model_dump(mode='json', exclude_none=True)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectMetadata':
        """Create instance from dictionary."""
        return cls.model_validate(data)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(exclude_none=True)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ProjectMetadata':
        """Create instance from JSON string."""
        return cls.model_validate_json(json_str)
    
    def validate_completeness(self) -> List[str]:
        """Validate completeness for Devpost submission."""
        missing_fields = []
        
        if not self.title:
            missing_fields.append('title')
        if not self.description or len(self.description) < 50:
            missing_fields.append('description (minimum 50 characters)')
        if not self.tags:
            missing_fields.append('tags')
        if not self.repository_url and not self.demo_url:
            missing_fields.append('repository_url or demo_url')
            
        return missing_fields


class SyncOperation(BaseModel):
    """Represents a synchronization operation."""
    
    operation_type: SyncOperationType
    target_field: str = Field(..., description="Field being synchronized")
    local_value: Any = Field(..., description="Local value")
    remote_value: Any = Field(None, description="Remote value")
    priority: int = Field(default=5, description="Operation priority (1-10)")
    timestamp: datetime = Field(default_factory=datetime.now)
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)
    error_message: Optional[str] = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        if not 1 <= v <= 10:
            raise ValueError('Priority must be between 1 and 10')
        return v
    
    @field_validator('max_retries')
    @classmethod
    def validate_max_retries(cls, v):
        if v < 0:
            raise ValueError('Max retries cannot be negative')
        return v
    
    @model_validator(mode='after')
    def validate_retry_count(self):
        if self.retry_count > self.max_retries:
            raise ValueError('Retry count cannot exceed max retries')
        return self
    
    def can_retry(self) -> bool:
        """Check if operation can be retried."""
        return self.retry_count < self.max_retries
    
    def increment_retry(self) -> None:
        """Increment retry count."""
        self.retry_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.model_dump(mode='json', exclude_none=True)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SyncOperation':
        """Create instance from dictionary."""
        return cls.model_validate(data)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(exclude_none=True)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SyncOperation':
        """Create instance from JSON string."""
        return cls.model_validate_json(json_str)


class FileChangeEvent(BaseModel):
    """Represents a file system change event."""
    
    file_path: Path
    change_type: ChangeType
    timestamp: datetime = Field(default_factory=datetime.now)
    affects_sync: bool = Field(default=True)
    file_size: Optional[int] = None
    checksum: Optional[str] = None
    content_type: Optional[str] = None
    content_hash: Optional[str] = None
    previous_content_hash: Optional[str] = None
    is_significant_change: bool = Field(default=True)
    media_metadata: Optional[Dict[str, Any]] = None
    git_info: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    @field_validator('file_size')
    @classmethod
    def validate_file_size(cls, v):
        if v is not None and v < 0:
            raise ValueError('File size cannot be negative')
        return v
    
    @model_validator(mode='after')
    def validate_deleted_file(self):
        if self.change_type == ChangeType.DELETED and self.file_size is not None:
            raise ValueError('Deleted files should not have file size')
        return self
    
    def is_media_file(self) -> bool:
        """Check if file is a media file."""
        media_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi', '.pdf', '.webp', '.svg'}
        return self.file_path.suffix.lower() in media_extensions
    
    def is_documentation_file(self) -> bool:
        """Check if file is a documentation file."""
        doc_patterns = ['readme', 'changelog', 'license', 'contributing', 'docs', 'documentation']
        filename_lower = self.file_path.name.lower()
        return (
            any(pattern in filename_lower for pattern in doc_patterns) or
            self.file_path.suffix.lower() in {'.md', '.txt', '.rst', '.adoc'} or
            'docs/' in str(self.file_path).lower()
        )
    
    def get_media_category(self) -> Optional[str]:
        """Get the category of media file."""
        if not self.is_media_file():
            return None
        
        suffix = self.file_path.suffix.lower()
        if suffix in {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}:
            return 'image'
        elif suffix in {'.mp4', '.mov', '.avi', '.webm', '.mkv'}:
            return 'video'
        elif suffix in {'.pdf', '.doc', '.docx'}:
            return 'document'
        else:
            return 'other'
    
    def is_configuration_file(self) -> bool:
        """Check if file is a configuration file."""
        config_files = {
            'package.json', 'pyproject.toml', 'requirements.txt', 'Dockerfile',
            'docker-compose.yml', 'docker-compose.yaml', '.env', 'config.json',
            'config.yaml', 'config.yml', 'setup.py', 'setup.cfg'
        }
        config_extensions = {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg'}
        
        return (
            self.file_path.name in config_files or
            self.file_path.suffix.lower() in config_extensions
        )
    
    def is_source_code_file(self) -> bool:
        """Check if file is source code."""
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala',
            '.html', '.css', '.scss', '.sass', '.less'
        }
        return self.file_path.suffix.lower() in code_extensions
    
    def should_trigger_sync(self, watch_patterns: List[str]) -> bool:
        """Check if file change should trigger sync based on patterns."""
        import fnmatch
        filename = self.file_path.name
        return any(fnmatch.fnmatch(filename, pattern) for pattern in watch_patterns)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.model_dump(mode='json', exclude_none=True)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileChangeEvent':
        """Create instance from dictionary."""
        return cls.model_validate(data)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(exclude_none=True)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'FileChangeEvent':
        """Create instance from JSON string."""
        return cls.model_validate_json(json_str)


class DevpostConfig(BaseModel):
    """Configuration for Devpost integration."""
    
    project_id: str = Field(..., description="Devpost project ID")
    hackathon_id: str = Field(..., description="Hackathon ID")
    auth_token: Optional[str] = Field(None, description="Authentication token")
    sync_enabled: bool = Field(default=True)
    watch_patterns: List[str] = Field(
        default_factory=lambda: ["README*", "*.md", "package.json", "pyproject.toml", "media/*"]
    )
    sync_interval: int = Field(default=300, description="Sync interval in seconds")
    auto_sync_media: bool = Field(default=True)
    notification_enabled: bool = Field(default=True)
    
    @field_validator('sync_interval')
    @classmethod
    def sync_interval_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Sync interval must be positive')
        if v < 60:
            raise ValueError('Sync interval must be at least 60 seconds')
        return v
    
    @field_validator('watch_patterns')
    @classmethod
    def validate_watch_patterns(cls, v):
        if not v:
            raise ValueError('At least one watch pattern is required')
        for pattern in v:
            if not pattern.strip():
                raise ValueError('Watch patterns cannot be empty')
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.model_dump(mode='json', exclude_none=True)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DevpostConfig':
        """Create instance from dictionary."""
        return cls.model_validate(data)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(exclude_none=True)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'DevpostConfig':
        """Create instance from JSON string."""
        return cls.model_validate_json(json_str)
    
    def validate_configuration(self) -> List[str]:
        """Validate configuration completeness."""
        issues = []
        
        if not self.project_id:
            issues.append('project_id is required')
        if not self.hackathon_id:
            issues.append('hackathon_id is required')
        if self.sync_enabled and not self.watch_patterns:
            issues.append('watch_patterns required when sync is enabled')
            
        return issues


class ProjectConnection(BaseModel):
    """Represents connection between local project and Devpost."""
    
    local_path: Path
    devpost_project_id: str
    hackathon_id: str
    last_sync: Optional[datetime] = None
    sync_status: SyncStatus = Field(default=SyncStatus.PENDING)
    configuration: DevpostConfig
    created_at: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)


@dataclass
class AuthToken:
    """Authentication token information."""
    access_token: str
    token_type: str = "Bearer"
    expires_at: Optional[datetime] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


@dataclass
class AuthResult:
    """Result of authentication operation."""
    success: bool
    token: Optional[AuthToken] = None
    error_message: Optional[str] = None
    requires_user_action: bool = False


@dataclass
class SyncResult:
    """Result of synchronization operation."""
    success: bool
    operations_completed: int = 0
    operations_failed: int = 0
    error_messages: List[str] = field(default_factory=list)
    sync_timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ValidationResult:
    """Result of validation operation."""
    is_valid: bool
    missing_fields: List[str] = field(default_factory=list)
    validation_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class PreviewResult:
    """Result of preview generation."""
    success: bool
    preview_html: Optional[str] = None
    preview_path: Optional[Path] = None
    validation_result: Optional[ValidationResult] = None
    error_message: Optional[str] = None