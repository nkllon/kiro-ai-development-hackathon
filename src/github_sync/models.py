"""
Core data models for GitHub synchronization.

This module defines the data structures used to represent GitHub entities
like repositories, issues, pull requests, and commits.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class IssueState(Enum):
    """GitHub issue states."""
    OPEN = "open"
    CLOSED = "closed"


class PullRequestState(Enum):
    """GitHub pull request states."""
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"


@dataclass
class Repository:
    """Represents a GitHub repository."""
    id: int
    name: str
    owner: str
    full_name: Optional[str] = None
    description: Optional[str] = None
    default_branch: str = "main"
    private: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_sync: Optional[datetime] = None
    clone_url: Optional[str] = None
    ssh_url: Optional[str] = None
    
    def __post_init__(self):
        """Validate repository data after initialization."""
        if not self.name or not self.owner:
            raise ValueError("Repository name and owner are required")
        if not self.full_name:
            self.full_name = f"{self.owner}/{self.name}"


@dataclass
class Issue:
    """Represents a GitHub issue."""
    id: int
    number: int
    title: str
    body: Optional[str] = None
    state: IssueState = IssueState.OPEN
    assignees: List[str] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    milestone: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    repository_id: int = 0
    author: Optional[str] = None
    comments_count: int = 0
    
    def __post_init__(self):
        """Validate issue data after initialization."""
        if not self.title:
            raise ValueError("Issue title is required")
        if isinstance(self.state, str):
            self.state = IssueState(self.state)


@dataclass
class PullRequest:
    """Represents a GitHub pull request."""
    id: int
    number: int
    title: str
    body: Optional[str] = None
    state: PullRequestState = PullRequestState.OPEN
    head_branch: str = ""
    base_branch: str = "main"
    head_sha: Optional[str] = None
    base_sha: Optional[str] = None
    mergeable: Optional[bool] = None
    merged: bool = False
    draft: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    repository_id: int = 0
    author: Optional[str] = None
    assignees: List[str] = field(default_factory=list)
    reviewers: List[str] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate pull request data after initialization."""
        if not self.title:
            raise ValueError("Pull request title is required")
        if not self.head_branch:
            raise ValueError("Head branch is required")
        if isinstance(self.state, str):
            self.state = PullRequestState(self.state)


@dataclass
class Commit:
    """Represents a Git commit."""
    sha: str
    message: str
    author: str
    author_email: str
    committed_at: Optional[datetime] = None
    repository_id: int = 0
    branch: str = "main"
    parents: List[str] = field(default_factory=list)
    files_changed: List[str] = field(default_factory=list)
    additions: int = 0
    deletions: int = 0
    
    def __post_init__(self):
        """Validate commit data after initialization."""
        if not self.sha or len(self.sha) < 7:
            raise ValueError("Valid commit SHA is required")
        if not self.message:
            raise ValueError("Commit message is required")
        if not self.author:
            raise ValueError("Commit author is required")


@dataclass
class WebhookEvent:
    """Represents a GitHub webhook event."""
    event_type: str
    action: str
    repository: Repository
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    processed: bool = False
    
    def __post_init__(self):
        """Validate webhook event data after initialization."""
        if not self.event_type:
            raise ValueError("Event type is required")
        if not self.action:
            raise ValueError("Event action is required")


@dataclass
class SyncResult:
    """Represents the result of a synchronization operation."""
    success: bool
    items_synced: int = 0
    items_updated: int = 0
    items_created: int = 0
    items_deleted: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    sync_duration: Optional[float] = None
    last_sync_time: Optional[datetime] = None
    
    def add_error(self, error: str) -> None:
        """Add an error message to the result."""
        self.errors.append(error)
        self.success = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message to the result."""
        self.warnings.append(warning)
    
    def merge(self, other: 'SyncResult') -> 'SyncResult':
        """Merge another sync result into this one."""
        return SyncResult(
            success=self.success and other.success,
            items_synced=self.items_synced + other.items_synced,
            items_updated=self.items_updated + other.items_updated,
            items_created=self.items_created + other.items_created,
            items_deleted=self.items_deleted + other.items_deleted,
            errors=self.errors + other.errors,
            warnings=self.warnings + other.warnings,
            sync_duration=(self.sync_duration or 0) + (other.sync_duration or 0),
            last_sync_time=max(
                self.last_sync_time or datetime.min,
                other.last_sync_time or datetime.min
            ) if self.last_sync_time or other.last_sync_time else None
        )


@dataclass
class DataConflict:
    """Represents a data synchronization conflict."""
    entity_type: str
    entity_id: str
    local_data: Dict[str, Any]
    remote_data: Dict[str, Any]
    conflict_fields: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolution_strategy: Optional[str] = None
    
    def __post_init__(self):
        """Validate conflict data after initialization."""
        if not self.entity_type or not self.entity_id:
            raise ValueError("Entity type and ID are required")
        if not self.conflict_fields:
            raise ValueError("At least one conflict field is required")


@dataclass
class ConflictResolution:
    """Represents the resolution of data conflicts."""
    conflicts_resolved: int = 0
    conflicts_remaining: int = 0
    resolution_strategy: str = "manual"
    resolutions: List[DataConflict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def add_resolution(self, conflict: DataConflict) -> None:
        """Add a resolved conflict."""
        conflict.resolved = True
        self.resolutions.append(conflict)
        self.conflicts_resolved += 1
    
    def add_error(self, error: str) -> None:
        """Add an error during conflict resolution."""
        self.errors.append(error)