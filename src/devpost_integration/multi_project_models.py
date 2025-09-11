#!/usr/bin/env python3
"""
Multi-Project Models - Multi-project management data classes

Extracted from models.py for RM-DDD compliance.
Single responsibility: Multi-project management data classes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any

from .core_models import (
    ConflictResolutionStrategy, CompletionStatus, NotificationSettings,
    DevpostConfig, Deadline
)


@dataclass
class ProjectConnection:
    """Local project to Devpost connection mapping."""
    local_project_id: str
    devpost_project_id: str
    connection_type: str = "primary"  # 'primary', 'backup', 'mirror'
    created_at: datetime = field(default_factory=datetime.now)
    last_synced: Optional[datetime] = None
    sync_status: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MultiProjectConfig:
    """Multi-project management configuration."""
    max_concurrent_projects: int = 5
    default_timeout: int = 300
    auto_save_interval: int = 60
    conflict_resolution_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.MANUAL
    project_isolation: bool = True
    shared_resources: List[str] = field(default_factory=list)
    project_connections: List[ProjectConnection] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ContextSwitchResult:
    """Multi-project context switch result."""
    success: bool
    from_project_id: Optional[str] = None
    to_project_id: Optional[str] = None
    switch_time: datetime = field(default_factory=datetime.now)
    context_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConflictResolution:
    """Multi-project conflict resolution result."""
    conflict_id: str
    project_ids: List[str]
    conflict_type: str
    resolution_strategy: ConflictResolutionStrategy
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None
    resolution_details: Optional[str] = None
    auto_resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProjectDashboard:
    """Multi-project dashboard data."""
    total_projects: int
    active_projects: int
    completed_projects: int
    projects: List[Dict[str, Any]] = field(default_factory=list)
    recent_activity: List[Dict[str, Any]] = field(default_factory=list)
    upcoming_deadlines: List[Deadline] = field(default_factory=list)
    system_status: str = "healthy"
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NotificationMessage:
    """Notification message data."""
    message_id: str
    title: str
    message: str
    notification_type: str
    priority: str = "normal"  # 'low', 'normal', 'high', 'urgent'
    created_at: datetime = field(default_factory=datetime.now)
    read: bool = False
    project_id: Optional[str] = None
    action_required: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReminderTiming:
    """Deadline reminder timing configuration."""
    reminder_id: str
    deadline_id: str
    reminder_times: List[datetime] = field(default_factory=list)
    notification_type: str = "email"
    enabled: bool = True
    custom_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GlobalSettings:
    """Global settings for multi-project management."""
    theme: str = "default"
    language: str = "en"
    timezone: str = "UTC"
    auto_sync: bool = True
    debug_mode: bool = False
    log_level: str = "INFO"
    max_log_files: int = 10
    backup_enabled: bool = True
    backup_interval: int = 24  # hours
    metadata: Dict[str, Any] = field(default_factory=dict)
